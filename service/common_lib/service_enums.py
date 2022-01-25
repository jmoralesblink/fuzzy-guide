from enum import Enum

from common_lib.enum_mixin import EnumMixin


class DeploymentEnvironments(EnumMixin, Enum):
    dev = "dev"
    local = "local"
    prod = "prod"
    staging = "staging"
    test = "test"
