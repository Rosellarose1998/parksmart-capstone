from datetime import datetime

from flask import Blueprint, g, jsonify, request
from sqlalchemy.orm import joinedload

from app.decorators import admin_required, login_required
from app.errors import ApiError
from app.models.reservation import Reservation
from app.models.user import UserRole
from app.serializers import reservation_to_dict
from app.services.reservation import cancel_reservation, create_reservation

reservations_bp = Blueprint("reservations", __name__, url_prefix="/api/v1/reservations")


def _parse_datetime(value: str, field: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ApiError(f"Invalid {field} datetime format", 422) from exc


@reservations_bp.post("")
@login_required
def create():
    data = request.get_json(silent=True) or {}
    if not data.get("spot_id") or not data.get("start_time") or not data.get("end_time"):
        raise ApiError("spot_id, start_time, and end_time are required", 422)

    reservation = create_reservation(
        g.db,
        g.current_user.id,
        spot_id=data["spot_id"],
        start_time=_parse_datetime(data["start_time"], "start_time"),
        end_time=_parse_datetime(data["end_time"], "end_time"),
    )
    return jsonify(reservation_to_dict(reservation)), 201


@reservations_bp.get("/me")
@login_required
def list_my_reservations():
    reservations = (
        g.db.query(Reservation)
        .options(joinedload(Reservation.spot), joinedload(Reservation.user))
        .filter(Reservation.user_id == g.current_user.id)
        .order_by(Reservation.start_time.desc())
        .all()
    )
    return jsonify([reservation_to_dict(r, include_relations=True) for r in reservations])


@reservations_bp.get("")
@admin_required
def list_all_reservations():
    reservations = (
        g.db.query(Reservation)
        .options(joinedload(Reservation.spot), joinedload(Reservation.user))
        .order_by(Reservation.created_at.desc())
        .all()
    )
    return jsonify([reservation_to_dict(r, include_relations=True) for r in reservations])


@reservations_bp.get("/<int:reservation_id>")
@login_required
def get_reservation(reservation_id: int):
    reservation = (
        g.db.query(Reservation)
        .options(joinedload(Reservation.spot), joinedload(Reservation.user))
        .filter(Reservation.id == reservation_id)
        .first()
    )
    if not reservation:
        raise ApiError("Reservation not found", 404)
    if reservation.user_id != g.current_user.id and g.current_user.role != UserRole.ADMIN:
        raise ApiError("Access denied", 403)
    return jsonify(reservation_to_dict(reservation, include_relations=True))


@reservations_bp.post("/<int:reservation_id>/cancel")
@login_required
def cancel(reservation_id: int):
    reservation = g.db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise ApiError("Reservation not found", 404)
    if reservation.user_id != g.current_user.id and g.current_user.role != UserRole.ADMIN:
        raise ApiError("Access denied", 403)
    reservation = cancel_reservation(g.db, reservation)
    return jsonify(reservation_to_dict(reservation))
