from typing import Union

import httpx
import yarl

__all__ = ("StrOrURL",)


StrOrURL = Union[str, yarl.URL, httpx.URL]
