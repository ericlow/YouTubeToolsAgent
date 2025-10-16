from datetime import datetime
from typing import Protocol


class Content(Protocol):
    source: str
    title: str
    author: str
    content: str
    creation_date: datetime
