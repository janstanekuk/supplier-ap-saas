from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID as UUIDType, Enum, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..database import Base
from decimal import Decimal

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    plan = Column(String, default="free")  # free, pro, enterprise
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="organization")

class UserRole(str, enum.Enum):
    admin = "admin"
    approver = "approver"
    processor = "processor"
    verifier = "verifier"
    member = "member"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_id = Column(String, unique=True, nullable=False)  # From Supabase Auth
    organization_id = Column(UUIDType(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, default=UserRole.member)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")

__all__ = ["Organization", "User", "UserRole", "Base"]

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUIDType(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    vat_number = Column(String, nullable=True)
    country_code = Column(String, default="GB")  # ISO country code
    payment_terms_days = Column(String, default="30")  # Net 30, Net 60, etc
    bank_account = Column(String, nullable=True)  # JSON field with bank details
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", foreign_keys=[organization_id])
    invoices = relationship("Invoice", back_populates="supplier")

class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    submitted = "submitted"
    matched = "matched"
    exception = "exception"
    approved = "approved"
    paid = "paid"

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(UUIDType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUIDType(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    supplier_id = Column(UUIDType(as_uuid=True), ForeignKey("suppliers.id"), nullable=False)
    
    # Invoice details
    invoice_number = Column(String, nullable=False)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    # Amounts (use Decimal for financial precision)
    gross_amount = Column(Numeric(15, 2), nullable=False)  # Total before VAT
    vat_rate = Column(Numeric(5, 2), default=20.00)  # Percentage
    vat_amount = Column(Numeric(15, 2), nullable=False)  # Calculated VAT
    total_amount = Column(Numeric(15, 2), nullable=False)  # gross + vat
    vat_country = Column(String, default="GB")
    reverse_charge = Column(Boolean, default=False)  # Reverse charge for VAT
    
    # Three-way matching
    po_matched = Column(Boolean, default=False)  # Matched to PO
    gr_matched = Column(Boolean, default=False)  # Matched to GR (Goods Receipt)
    status = Column(String, default=InvoiceStatus.draft)  # Status enum
    
    # Metadata
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", foreign_keys=[organization_id])
    supplier = relationship("Supplier", back_populates="invoices")