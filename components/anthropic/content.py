from datetime import datetime
from typing import Protocol

"""
Content Interface
"""
class Content(Protocol):
    source: str
    title: str
    author: str
    content: str
    creation_date: datetime
