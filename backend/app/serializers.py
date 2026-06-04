from datetime import datetime

from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.user import User


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "created_at": _iso(user.created_at),
    }


def lot_to_dict(lot: ParkingLot) -> dict:
    return {
        "id": lot.id,
        "name": lot.name,
        "address": lot.address,
        "description": lot.description,
        "created_at": _iso(lot.created_at),
    }


def spot_to_dict(spot: ParkingSpot) -> dict:
    return {
        "id": spot.id,
        "lot_id": spot.lot_id,
        "spot_number": spot.spot_number,
        "status": spot.status.value,
        "spot_type": spot.spot_type.value,
        "created_at": _iso(spot.created_at),
    }


def reservation_to_dict(reservation: Reservation, *, include_relations: bool = False) -> dict:
    data = {
        "id": reservation.id,
        "user_id": reservation.user_id,
        "spot_id": reservation.spot_id,
        "start_time": _iso(reservation.start_time),
        "end_time": _iso(reservation.end_time),
        "status": reservation.status.value,
        "created_at": _iso(reservation.created_at),
    }
    if include_relations:
        if reservation.spot is not None:
            data["spot"] = spot_to_dict(reservation.spot)
        if reservation.user is not None:
            data["user"] = user_to_dict(reservation.user)
    return data
