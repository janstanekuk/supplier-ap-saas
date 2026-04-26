from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class InvoiceCreate(BaseModel):
    supplier_id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    gross_amount: Decimal
    vat_rate: Decimal = 20.00
    vat_country: str = "GB"
    reverse_charge: bool = False
    notes: Optional[str] = None

class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    gross_amount: Optional[Decimal] = None
    vat_rate: Optional[Decimal] = None
    vat_country: Optional[str] = None
    reverse_charge: Optional[bool] = None
    notes: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: str
    supplier_id: str
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    gross_amount: Decimal
    vat_rate: Decimal
    vat_amount: Decimal
    total_amount: Decimal
    vat_country: str
    reverse_charge: bool
    po_matched: bool
    gr_matched: bool
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True