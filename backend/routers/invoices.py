from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
import uuid
from datetime import datetime

from ..database import get_db
from ..models import Invoice, Supplier, InvoiceStatus
from ..schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from ..services.vat import calculate_vat, validate_three_way_match

router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])

async def get_org_id_from_request(request: Request) -> str:
    """Get organization_id from JWT token"""
    if not hasattr(request.state, 'organization_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No organization context"
        )
    return request.state.organization_id

@router.post("", response_model=InvoiceResponse)
async def create_invoice(
    invoice: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Create new invoice"""
    # Verify supplier belongs to organization
    result = await db.execute(
        select(Supplier).where(
            (Supplier.id == invoice.supplier_id) &
            (Supplier.organization_id == org_id)
        )
    )
    supplier = result.scalar_one_or_none()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    # Calculate VAT
    vat_amount, total_amount = calculate_vat(
        invoice.gross_amount,
        invoice.vat_rate,
        invoice.reverse_charge
    )
    
    # Create invoice
    db_invoice = Invoice(
        id=uuid.uuid4(),
        organization_id=org_id,
        supplier_id=invoice.supplier_id,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        gross_amount=invoice.gross_amount,
        vat_rate=invoice.vat_rate,
        vat_amount=vat_amount,
        total_amount=total_amount,
        vat_country=invoice.vat_country,
        reverse_charge=invoice.reverse_charge,
        notes=invoice.notes,
        status=InvoiceStatus.draft
    )
    
    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice

@router.get("", response_model=list[InvoiceResponse])
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request),
    status: str = None,
    skip: int = 0,
    limit: int = 100
):
    """List invoices with optional status filter"""
    query = select(Invoice).where(Invoice.organization_id == org_id)
    
    if status:
        query = query.where(Invoice.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    invoices = result.scalars().all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Get specific invoice"""
    result = await db.execute(
        select(Invoice).where(
            (Invoice.id == invoice_id) &
            (Invoice.organization_id == org_id)
        )
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    invoice_update: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Update invoice"""
    result = await db.execute(
        select(Invoice).where(
            (Invoice.id == invoice_id) &
            (Invoice.organization_id == org_id)
        )
    )
    db_invoice = result.scalar_one_or_none()
    
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Update fields
    update_data = invoice_update.dict(exclude_unset=True)
    
    # Recalculate VAT if amounts changed
    if 'gross_amount' in update_data or 'vat_rate' in update_data or 'reverse_charge' in update_data:
        gross = update_data.get('gross_amount', db_invoice.gross_amount)
        rate = update_data.get('vat_rate', db_invoice.vat_rate)
        reverse = update_data.get('reverse_charge', db_invoice.reverse_charge)
        
        vat_amount, total_amount = calculate_vat(gross, rate, reverse)
        update_data['vat_amount'] = vat_amount
        update_data['total_amount'] = total_amount
    
    for field, value in update_data.items():
        setattr(db_invoice, field, value)
    
    db_invoice.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_invoice)
    return db_invoice

@router.post("/{invoice_id}/match-po", response_model=InvoiceResponse)
async def match_po(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Mark invoice as PO matched"""
    result = await db.execute(
        select(Invoice).where(
            (Invoice.id == invoice_id) &
            (Invoice.organization_id == org_id)
        )
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    invoice.po_matched = True
    
    # Check three-way match
    if invoice.po_matched and invoice.gr_matched:
        invoice.status = InvoiceStatus.matched
    else:
        invoice.status = InvoiceStatus.exception
    
    invoice.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(invoice)
    return invoice

@router.post("/{invoice_id}/match-gr", response_model=InvoiceResponse)
async def match_gr(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Mark invoice as GR (Goods Receipt) matched"""
    result = await db.execute(
        select(Invoice).where(
            (Invoice.id == invoice_id) &
            (Invoice.organization_id == org_id)
        )
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    invoice.gr_matched = True
    
    # Check three-way match
    if invoice.po_matched and invoice.gr_matched:
        invoice.status = InvoiceStatus.matched
    else:
        invoice.status = InvoiceStatus.exception
    
    invoice.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(invoice)
    return invoice

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: str,
    db: AsyncSession = Depends(get_db),
    org_id: str = Depends(get_org_id_from_request)
):
    """Delete invoice"""
    result = await db.execute(
        select(Invoice).where(
            (Invoice.id == invoice_id) &
            (Invoice.organization_id == org_id)
        )
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    await db.delete(invoice)
    await db.commit()
    return None