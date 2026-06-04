from flask import Blueprint, g, jsonify, request

from app.decorators import login_required, with_db
from app.errors import ApiError
from app.models.user import User
from app.serializers import user_to_dict
from app.utils.auth import authenticate_user, create_access_token, hash_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


def _require_fields(data: dict, *fields: str) -> None:
    missing = [f for f in fields if f not in data or data[f] in (None, "")]
    if missing:
        raise ApiError(f"Missing required fields: {', '.join(missing)}", 422)


@auth_bp.post("/register")
@with_db
def register():
    data = request.get_json(silent=True) or {}
    _require_fields(data, "email", "password", "full_name")

    if len(data["password"]) < 8:
        raise ApiError("Password must be at least 8 characters", 422)

    existing = g.db.query(User).filter(User.email == data["email"]).first()
    if existing:
        raise ApiError("Email already registered", 409)

    user = User(
        email=data["email"],
        hashed_password=hash_password(data["password"]),
        full_name=data["full_name"],
    )
    g.db.add(user)
    g.db.commit()
    g.db.refresh(user)
    return jsonify(user_to_dict(user)), 201


@auth_bp.post("/login")
@with_db
def login():
    data = request.get_json(silent=True) or {}
    _require_fields(data, "email", "password")

    user = authenticate_user(g.db, data["email"], data["password"])
    if not user:
        raise ApiError("Invalid email or password", 401)
    if not user.is_active:
        raise ApiError("Account is deactivated", 403)

    token = create_access_token(subject=user.email, role=user.role.value)
    return jsonify({"access_token": token, "token_type": "bearer"})


@auth_bp.get("/me")
@login_required
def get_me():
    return jsonify(user_to_dict(g.current_user))
