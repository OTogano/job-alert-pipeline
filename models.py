import hashlib
import re

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional

class Remote(Enum):
    yes = auto()
    no = auto()
    hybrid = auto()

@dataclass
class Job:
    title: str
    company: str
    url: str
    location: Optional[str]
    remote: Optional[Remote]
    tags: Optional[list[str]]
    source: str
    posted_date: datetime
    id: str 

    @classmethod
    def from_dict(cls, data: dict, source: str):
        hash_id = hashlib.sha256(f"{data['url']}{source}".encode()).hexdigest()
        format_date = datetime.fromisoformat(data['date'])
        remote_status = _parse_remote_status(data.get('remote'))
        
        return cls(
            title = data['title'],
            company = data['company'],
            url = data['url'],
            location = data.get('location'),
            remote = remote_status,
            tags = data.get('tags'),
            source = source,
            posted_date = format_date,
            id = hash_id,
        )
    
def _parse_remote_status(raw_value):
    if raw_value == True:
        return Remote.yes
    elif raw_value == False:
        return Remote.no
    else:
        return None