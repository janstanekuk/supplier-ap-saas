from decimal import Decimal

def calculate_vat(gross_amount: Decimal, vat_rate: Decimal, reverse_charge: bool = False) -> tuple[Decimal, Decimal]:
    """
    Calculate VAT and total amount
    Returns: (vat_amount, total_amount)
    """
    if reverse_charge:
        # No VAT if reverse charge applies
        return Decimal('0.00'), gross_amount
    
    vat_amount = (gross_amount * vat_rate / Decimal('100')).quantize(Decimal('0.01'))
    total_amount = (gross_amount + vat_amount).quantize(Decimal('0.01'))
    
    return vat_amount, total_amount

def validate_three_way_match(po_matched: bool, gr_matched: bool) -> str:
    """
    Validate three-way matching
    Returns: status (matched, exception, draft)
    """
    if not po_matched or not gr_matched:
        return "exception"
    return "matched"