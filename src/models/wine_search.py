from pydantic import BaseModel, Field
from typing import Optional

class SearchWinePriceList(BaseModel):
    name: str = Field(default=None)
    country: str = Field(default=None)
    acidity: str = Field(default=None)
    color: str = Field(default=None)
    sort_order: str = Field(default=None)
    what_to_return: str = Field(default=None)

    def process(self, session_id):
        from src.domain.wine_price_list import find_wines
        return find_wines(self)