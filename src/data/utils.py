"""Shared utility functions for data repositories."""
from __future__ import annotations
import hashlib


def hash_password(password: str) -> str:
    """SHA-256 hash a password string."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def build_initials(name: str) -> str:
    """Build 1-2 letter initials from a full name."""
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()
