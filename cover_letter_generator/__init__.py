"""Generate journal cover letters from structured metadata."""
from .core import TEMPLATES, REQUIRED, validate, render

__version__ = "0.1.0"
__all__ = ["TEMPLATES", "REQUIRED", "validate", "render"]
