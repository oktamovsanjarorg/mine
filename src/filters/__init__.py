from .admin import IsAdmin
from .private import IsPrivateChat
from .content import HasURL, HasDocument, HasPhoto, HasVoice, IsForwarded

__all__ = [
    "IsAdmin",
    "IsPrivateChat",
    "HasURL",
    "HasDocument",
    "HasPhoto",
    "HasVoice",
    "IsForwarded"
]
