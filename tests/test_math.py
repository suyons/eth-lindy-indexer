import pytest
from decimal import Decimal
from indexer.utils.math import wei_to_ether, ether_to_wei, format_ether

def test_wei_to_ether_standard():
    assert wei_to_ether(10**18) == Decimal("1")
    assert wei_to_ether("500000000000000000") == Decimal("0.5")

def test_ether_to_wei_standard():
    assert ether_to_wei(1) == 10**18
    assert ether_to_wei("0.5") == 500000000000000000
    assert ether_to_wei(0.1) == 100000000000000000

def test_high_precision_large_value():
    # Max uint256
    max_uint256 = 2**256 - 1
    eth = wei_to_ether(max_uint256)
    
    # Check if we can convert back exactly
    assert ether_to_wei(eth) == max_uint256
    
    # Check precision
    assert format_ether(eth, 18).endswith("584007913129639935")

def test_wei_to_ether_precision():
    wei = 1
    eth = wei_to_ether(wei)
    assert format_ether(eth, 18) == "0.000000000000000001"
