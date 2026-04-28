"""APP API Models"""

# ruff: noqa: F403
from .base import PixivBaseModel
from .illust import *
from .novel import *
from .other import *
from .param import *
from .user import *

for cls in PixivBaseModel.__subclasses__():
    cls.model_rebuild()
