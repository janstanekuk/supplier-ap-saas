from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class SupplierCreate(BaseModel):
    name: str
    vat_number: Optional[str] = None
    country_code: str = "GB"
    payment_terms_days: str = "30"
    bank_account: Optional[str] = None

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    vat_number: Optional[str] = None
    country_code: Optional[str] = None
    payment_terms_days: Optional[str] = None
    bank_account: Optional[str] = None
    is_active: Optional[bool] = None

class SupplierResponse(BaseModel):
    id: str  # Convert UUID to string
    name: str
    vat_number: Optional[str]
    country_code: str
    payment_terms_days: str
    bank_account: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)