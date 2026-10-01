"""
Shared utility helpers for LegalAI backend.
"""


def get_user_id(current_user: dict) -> str:
    """Safely extract user_id from the current_user dependency dict.

    The get_current_user dependency may return user_id under different keys
    depending on how the JWT was issued. This helper handles all variants.
    """
    uid = (
        current_user.get("user_id")
        or current_user.get("id")
        or current_user.get("sub")
    )
    if not uid:
        raise ValueError("Could not determine user_id from token payload")
    return str(uid)
