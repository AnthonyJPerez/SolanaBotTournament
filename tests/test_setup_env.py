import pytest
from setup_env import validate_solana_address


def test_validate_solana_address_valid():
    # Test valid Solana addresses
    valid_addresses = [
        "11111111111111111111111111111112",  # System program
        "So11111111111111111111111111111111111111112",  # Wrapped SOL
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
        "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"   # Example address
    ]
    
    for addr in valid_addresses:
        assert validate_solana_address(addr), f"Should be valid: {addr}"


def test_validate_solana_address_invalid():
    # Test invalid Solana addresses
    invalid_addresses = [
        "",  # Empty
        "short",  # Too short
        "0" * 50,  # Too long and invalid characters
        "111111111111111111111111111111110",  # Contains '0' (invalid base58)
        "111111111111111111111111111111111O",  # Contains 'O' (invalid base58)
        "111111111111111111111111111111111I",  # Contains 'I' (invalid base58)
        "111111111111111111111111111111111l",  # Contains 'l' (invalid base58)
        "your_wallet_address_here",  # Placeholder text
        "abc123",  # Too short
    ]
    
    for addr in invalid_addresses:
        assert not validate_solana_address(addr), f"Should be invalid: {addr}"


def test_validate_solana_address_edge_cases():
    # Test edge cases
    assert not validate_solana_address(None)
    assert not validate_solana_address("   ")  # Whitespace only
    
    # Test minimum and maximum valid lengths
    min_valid = "1" * 32  # Minimum length
    max_valid = "1" * 44  # Maximum length
    
    assert validate_solana_address(min_valid)
    assert validate_solana_address(max_valid)
    
    # Test just outside valid range
    too_short = "1" * 31
    too_long = "1" * 45
    
    assert not validate_solana_address(too_short)
    assert not validate_solana_address(too_long)