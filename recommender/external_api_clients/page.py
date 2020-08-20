from __future__ import annotations
from dataclasses import dataclass
from typing import Final

@dataclass
class Page:
    limit: int
    offset: int

    def next_page(self) -> Page:
        return Page(limit=self.limit, offset=self.offset + self.limit)

FIRST_PAGE: Final[Page] = Page(limit=20, offset=0)

