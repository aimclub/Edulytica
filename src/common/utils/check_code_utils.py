"""
This module provides utility functions for generating one-time verification codes.

Functions:
    generate_code: Generates a 6-digit numeric verification code.
"""
from random import randint


def generate_code():
    """
    Generates a 6-digit numeric verification code as a string.

    Returns:
        str: A 6-digit numeric string representing the verification code.
    """
    return str(randint(1000000, 9999999))[1:]
