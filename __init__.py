"""
Secure Weather Station - IoT Security Project
Utah Valley University

This package provides a comprehensive IoT security education project.
"""

__version__ = '1.0.0'
__author__ = 'UVU IoT Security Lab'

# Make key modules easily importable
from security import JWTManager, SecureDataTransmission, InputValidator, SecureCredentialStore
from config import settings

__all__ = [
    'JWTManager',
    'SecureDataTransmission',
    'InputValidator', 
    'SecureCredentialStore',
    'settings'
]
