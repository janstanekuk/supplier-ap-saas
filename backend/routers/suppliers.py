from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from datetime import datetime

from ..database import get_db
from ..models import Supplier, Organization
from ..schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])

async def get_org_id_from_request(request: Request) -> str:
    """Get organization_id from JWT token in request"""
    if not hasattr(request.state, 'organization_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No organization context"
        )
    return request.state.organization_id

@router.post("", response_model=SupplierResponse)
async def create_supplier(
    supplier: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Create new supplier (multi-tenant: org_id isolation)"""
    db_supplier = Supplier(
        id=uuid.uuid4(),
        organization_id=org_id,
        **supplier.dict()
    )
    db.add(db_supplier)
    await db.commit()
    await db.refresh(db_supplier)
    
    # Convert to response with string IDs
    return {
        "id": str(db_supplier.id),
        "name": db_supplier.name,
        "vat_number": db_supplier.vat_number,
        "country_code": db_supplier.country_code,
        "payment_terms_days": db_supplier.payment_terms_days,
        "bank_account": db_supplier.bank_account,
        "is_active": db_supplier.is_active,
        "created_at": db_supplier.created_at,
        "updated_at": db_supplier.updated_at,
    }

@router.get("", response_model=list[SupplierResponse])
async def list_suppliers(
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request),
    skip: int = 0,
    limit: int = 100
):
    """List all suppliers for organization"""
    result = await db.execute(
        select(Supplier)
        .where(Supplier.organization_id == org_id)
        .offset(skip)
        .limit(limit)
    )
    suppliers = result.scalars().all()
    
    # Convert to response with string IDs
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "vat_number": s.vat_number,
            "country_code": s.country_code,
            "payment_terms_days": s.payment_terms_days,
            "bank_account": s.bank_account,
            "is_active": s.is_active,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
        }
        for s in suppliers
    ]

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Get specific supplier (must belong to user's org)"""
    result = await db.execute(
        select(Supplier).where(
            (Supplier.id == supplier_id) &
            (Supplier.organization_id == org_id)
        )
    )
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return {
        "id": str(supplier.id),
        "name": supplier.name,
        "vat_number": supplier.vat_number,
        "country_code": supplier.country_code,
        "payment_terms_days": supplier.payment_terms_days,
        "bank_account": supplier.bank_account,
        "is_active": supplier.is_active,
        "created_at": supplier.created_at,
        "updated_at": supplier.updated_at,
    }

@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    supplier_update: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Update supplier"""
    result = await db.execute(
        select(Supplier).where(
            (Supplier.id == supplier_id) &
            (Supplier.organization_id == org_id)
        )
    )
    db_supplier = result.scalar_one_or_none()
    
    if not db_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Update only provided fields
    update_data = supplier_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    
    db_supplier.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_supplier)
    
    return {
        "id": str(db_supplier.id),
        "name": db_supplier.name,
        "vat_number": db_supplier.vat_number,
        "country_code": db_supplier.country_code,
        "payment_terms_days": db_supplier.payment_terms_days,
        "bank_account": db_supplier.bank_account,
        "is_active": db_supplier.is_active,
        "created_at": db_supplier.created_at,
        "updated_at": db_supplier.updated_at,
    }

@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Delete supplier (soft delete - set is_active=False)"""
    result = await db.execute(
        select(Supplier).where(
            (Supplier.id == supplier_id) &
            (Supplier.organization_id == org_id)
        )
    )
    db_supplier = result.scalar_one_or_none()
    
    if not db_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Soft delete
    db_supplier.is_active = False
    db_supplier.updated_at = datetime.utcnow()
    await db.commit()
    return None
