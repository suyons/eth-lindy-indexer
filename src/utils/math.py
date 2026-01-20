import decimal
from decimal import Decimal
from typing import Union

# Set precision high enough to handle uint256 (max ~1.15e77)
decimal.getcontext().prec = 80

WEI_PER_ETHER = Decimal("1000000000000000000")

def wei_to_ether(wei_value: Union[int, str, Decimal]) -> Decimal:
    """
    Convert Wei (integer) to Ether (Decimal) with high precision.
    """
    return Decimal(wei_value) / WEI_PER_ETHER

def ether_to_wei(ether_value: Union[int, str, float, Decimal]) -> int:
    """
    Convert Ether (Decimal/float/str) to Wei (int) with high precision.
    """
    # Use quantize to avoid floating point issues if a float was passed
    wei_decimal = (Decimal(str(ether_value)) * WEI_PER_ETHER).quantize(Decimal("1"))
    return int(wei_decimal)

def format_ether(ether_value: Decimal, places: int = 18) -> str:
    """
    Format a Decimal Ether value to a string with specified decimal places.
    """
    return f"{ether_value:.{places}f}"