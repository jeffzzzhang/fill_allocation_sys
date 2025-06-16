from typing import Union
from pydantic import BaseModel

class Fills(BaseModel):
    stock_ticker: str
    price: Union[int, float]
    quantity: Union[int, float]
