from functools import wraps

from flask import Blueprint, g, jsonify, request

from app.database import get_db
from app.models.user import User, UserRole
from app.utils.auth import decode_access_token


def _get_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def with_db(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        db = get_db()
        try:
            g.db = db
            return f(*args, **kwargs)
        finally:
            db.close()

    return decorated


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_token()
        if not token:
            return jsonify({"detail": "Missing authorization token"}), 401

        payload = decode_access_token(token)
        if not payload or "sub" not in payload:
            return jsonify({"detail": "Invalid or expired token"}), 401

        db = get_db()
        try:
            user = db.query(User).filter(User.email == payload["sub"]).first()
            if not user or not user.is_active:
                return jsonify({"detail": "User not found or inactive"}), 401
            g.current_user = user
            g.db = db
            return f(*args, **kwargs)
        finally:
            db.close()

    return decorated


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if g.current_user.role != UserRole.ADMIN:
            return jsonify({"detail": "Admin access required"}), 403
        return f(*args, **kwargs)

    return decorated
