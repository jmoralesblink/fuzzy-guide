import os
import importlib


# read in the current environment, defaulting to local
ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")

# read in any personal settings, as the highest priority (must be at the end of the file
if ENVIRONMENT == "local" and os.path.exists("django_service_bootstrap/settings/personal.py"):
    ENVIRONMENT = "personal"

# dynamically import the correct file with the same name as the environment, and add to the global namespace
# this is equivalent to `from .local import *`, but is dynamic
settings_module = importlib.import_module(f".{ENVIRONMENT}", package=__name__)
all_names = [name for name in dir(settings_module) if not name.startswith("_")]
globals().update({name: getattr(settings_module, name) for name in all_names})
