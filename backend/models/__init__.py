from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID as UUIDType, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..database import Base

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