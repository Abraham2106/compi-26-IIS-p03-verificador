"""Explorador reutilizable de la etapa anterior.

Los consumidores usan los mismos Token y TokenType, sin catalogos paralelos.
"""

from .errores import ErrorLexico
from .scanner import Scanner
from .tokens import Token, TokenType

__all__ = ["Scanner", "Token", "TokenType", "ErrorLexico"]
