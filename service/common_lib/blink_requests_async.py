"""This file has functionality that roughly matches blink-requests, but uses HTTPX, allowing async calls"""
import asyncio
import logging
import threading
import math
from functools import wraps
from importlib import import_module
from time import time

import httpx
from common_lib.errors import ClientError, BlinkParsingError
from django.conf import settings
from httpx import Response
from respx.transports import MockTransport
from blink_logging_metrics.metrics import statsd
import re

from common_lib.service_enums import DeploymentEnvironments

_logger = logging.getLogger(__name__)
_disallowed_headers = {"authorization", "ocp-apim-subscription-key"}  # must be lower-case
_thread_local = threading.local()
_max_body_size_to_log = getattr(settings, "HTTP_MAX_LOG_PAYLOAD", 2000)
_log_headers = getattr(settings, "HTTP_LOG_HEADERS", True)


def _sanitize_headers(headers):
    """
    Cleans the headers to prevent sensitive information from being logged
    :param headers: the headers to process
    :return: sanitized copy of the headers dictionary
    """
    sanitized_headers = {
        header_name: header_value
        for header_name, header_value in headers.items()
        if header_name.lower() not in _disallowed_headers
    }
    return sanitized_headers


def _get_request_body(request):
    """
    Truncates the request body if necessary for logging
    """
    request.read()
    content = getattr(request, "content", None) or ""

    if content and len(content) > _max_body_size_to_log:
        truncated_body = content[:_max_body_size_to_log]
        if isinstance(truncated_body, bytes):
            truncated_body += b"..."
        elif isinstance(truncated_body, str):
            truncated_body += "..."
        return truncated_body

    return content


def _get_response_body(response):
    """
    Truncates the response body if necessary for logging
    """
    content = getattr(response, "text", None) or ""

    # if the response is too long, we can't parse partial json, so just return the first part as a string
    if len(content) > _max_body_size_to_log:
        content = content[:_max_body_size_to_log] + "..."

    return content


def _record_metrics(request, response, duration_ms):
    """Record metrics for outbound responses"""
    statsd_tags = [
        f"status_code:{response.status_code}",
        f"method:{request.method}",
        f"endpoint:{request.url.host}",
    ]
    statsd.timing("http.request.duration", duration_ms, tags=statsd_tags)
    status_code_range = int((math.floor(response.status_code / 100)) * 100)
    statsd.increment(f"http.request.status.{status_code_range}", tags=statsd_tags)


def _log_request(request, log_body: bool = True):
    request_extra = {
        "method": request.method,
        "url": request.url,
    }
    if _log_headers:
        request_extra["headers"] = _sanitize_headers(request.headers)
    if log_body:
        request_extra["body"] = _get_request_body(request)
    _logger.info(f"S=> {request.method} - {request.url}", extra=request_extra)
    request.start_time = time()


async def _log_request_async(request):
    _log_request(request)


def _log_request_no_body(request):
    _log_request(request, log_body=False)


async def _log_request_no_body_async(request):
    _log_request(request, log_body=False)


def _log_response(response, log_body: bool = True):
    # get the initial request, handling and warning if there was a redirect
    request = response.request
    if response.history:
        request = response.history[0].request
        _logger.warning(f"Got a redirect from url: {request.url}")

    duration = round((time() - request.start_time) * 1000)  # duration in milliseconds
    response_extra = {
        "method": request.method,
        "url": request.url,
        "duration": duration,
        "status_code": response.status_code,
    }
    if _log_headers:
        response_extra["headers"] = _sanitize_headers(response.headers)
    if log_body:
        response_extra["body"] = _get_response_body(response)
    _logger.info(f"S<= {request.method} ({response.status_code}) - {request.url}", extra=response_extra)
    _record_metrics(request, response, duration)


async def _log_response_async(response):
    _log_response(response)


def _log_response_no_body(response):
    _log_response(response, log_body=False)


async def _log_response_no_body_async(response):
    _log_response(response)


def _add_correlation_id_header(request):
    cur_thread = threading.current_thread()
    if hasattr(cur_thread, "blink_correlation_id"):
        # convert to a string, since a UUID can't be encoded to a header
        request.headers["Blink-Correlation-Id"] = str(cur_thread.blink_correlation_id)


async def _add_correlation_id_header_async(request):
    _add_correlation_id_header(request)


def _get_config(config_name: str, is_async: bool):
    settings_config = settings.HTTP_CLIENTS["endpoints"][config_name]

    # setup the config dict (an async client needs async hook methods)
    log_body = settings_config.get("log_body", True)
    if is_async:
        req_logger = _log_request_async if log_body else _log_request_no_body_async
        resp_logger = _log_response_async if log_body else _log_response_no_body_async
        config = {"event_hooks": {"request": [req_logger, _add_correlation_id_header_async], "response": [resp_logger]}}
    else:
        req_logger = _log_request if log_body else _log_request_no_body
        resp_logger = _log_response if log_body else _log_response_no_body
        config = {"event_hooks": {"request": [req_logger, _add_correlation_id_header], "response": [resp_logger]}}

    if "root_url" in settings_config:
        config["base_url"] = settings_config["root_url"]
    if "auth" in settings_config:
        config["auth"] = (settings_config["auth"]["username"], settings_config["auth"]["password"])
    if "default_timeout_seconds" in settings_config:
        config["timeout"] = settings_config["default_timeout_seconds"]
    if "num_retries" in settings_config:
        transport_class = httpx.AsyncHTTPTransport if is_async else httpx.HTTPTransport
        config["transport"] = transport_class(retries=settings_config["num_retries"])
    if "mocked_transport" in settings_config and settings_config["mocked_transport"]:
        path = settings_config["mocked_transport"]["path"]
        name = settings_config["mocked_transport"]["name"]
        router = getattr(import_module(path), name)
        config["transport"] = MockTransport(router=router)
    return config


def get_response(response: Response, allow_non_200: bool = False, as_json: bool = False):
    # Checks if response status in 2xx range or if manually allowing non 200 statuses. If so, return response in json.
    if response.status_code >= 300 and not allow_non_200:
        raise ClientError(
            f"Received status code {response.status_code} back from {response.request.url} with the following response: {response.text}"
        )
    try:
        if as_json:
            return response.json()
        return response.text
    except Exception as ex:
        _logger.error("Could not turn response to json", ex)
        raise BlinkParsingError()


def get_client(client_name: str, is_async: bool = False):
    """
    Get a persistent client, with a connection-pool, and unique for each thread

    The client should not be closed, so it can be re-used between requests.  This won't work when using runserver, but
    if you are using the run_async_as_sync decorator, it will automatically handle that for you.
    """
    # get the thread's list of clients, creating it if it doesn't already exist
    client_attr = "httpx_async_clients" if is_async else "httpx_clients"
    thread_clients = getattr(_thread_local, client_attr, {})
    if not thread_clients:
        setattr(_thread_local, client_attr, thread_clients)

    # get the existing client if it exists, or create a new one
    client = thread_clients.get(client_name, None)
    if client is None:
        config = _get_config(client_name, is_async)
        client = httpx.AsyncClient(**config) if is_async else httpx.Client(**config)
        thread_clients[client_name] = client

    return client


def get_event_loop():
    """Retrieves a running event loop and if one not found, creates a new event loop"""
    try:
        # if there is not already an event loop, this will raise an error when called outside of the main thread, so
        # catch it and create a new event loop, and set it as the default for the thread
        loop = asyncio.get_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def run_async_as_sync(async_func):
    """
    Run an async function synchronously, returning its result when it completes.

    This is similar to the asgiref @async_to_sync function that Django uses, but this does not close the event loop
    when it completes, allowing future calls/requests to use the same one.  This is critical, because async clients
    created on one loop cannot be used on a different one, so they need to be closed after each request.  This causes
    a delay of about 20-25 ms, but under heavy load can double latency for the endpoint.

    When running with runserver, it will close the event loop after each request, causing warnings about not closing
    the HTTPX client(s).  This will automatically close all async clients before returning, when running with runserver,
    so the clients are closed properly.  When running with gunicorn, it will leave them open, so they can be re-used.
    """

    async def close_thread_clients():
        thread_clients = getattr(_thread_local, "httpx_async_clients", {})

        for client_name in list(thread_clients.keys()):
            await thread_clients[client_name].aclose()
            del thread_clients[client_name]

    @wraps(async_func)
    def decorator(*args, **kwargs):
        # get an existing event loop, or create a new one
        loop = get_event_loop()

        # run the decorated function
        try:
            result = loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            # clean up any async httpx clients from this thread, if using runserver or running unit tests
            if settings.IS_RUN_SERVER or settings.ENVIRONMENT == DeploymentEnvironments.test.value:
                loop.run_until_complete(close_thread_clients())

        return result

    return decorator
