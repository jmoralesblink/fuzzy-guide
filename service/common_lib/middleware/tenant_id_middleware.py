from django.utils.functional import SimpleLazyObject


def get_user_tenant_id(request):
    return getattr(request.user, "tenant_id", None)


class TenantIdMiddleware(object):
    """
    Add a tenant_id attribute to each request, which will be accessible while processing the request.

    Due to how DRF handles authentication in the view layer, the user is not accessible in middleware until after the
    response is returned, so this creates a lazy object that will work when accessed in view code, but not if called
    in middleware before the request is processed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant_id = SimpleLazyObject(lambda: get_user_tenant_id(request))
        # process the request and return the response
        return self.get_response(request)
