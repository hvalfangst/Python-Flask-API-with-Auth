from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel, Field


class CreateAccountRequest(BaseModel):
    user_id: int
    account_number: str = Field(min_length=12, max_length=12)
    balance: Optional[Decimal] = Field(ge=0.00, precision=2)


class UpdateAccountRequest(BaseModel):
    balance: Optional[Decimal] = Field(ge=0.00, precision=2)


class Account:
    def __init__(self, account_id, user_id, account_number, balance):
        self.account_id = account_id
        self.user_id = user_id
        self.account_number = account_number
        self.balance = balance

    def to_dict(self) -> Dict[str, str]:
        return {
            "account_id": self.account_id,
            "user_id": self.user_id,
            "account_number": self.account_number,
            "balance": self.balance
        }