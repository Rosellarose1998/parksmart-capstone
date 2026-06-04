from flask import Blueprint, g, jsonify, request

from app.decorators import admin_required
from app.errors import ApiError
from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot, SpotStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User, UserRole
from app.serializers import user_to_dict
from app.utils.auth import hash_password

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.get("/dashboard")
@admin_required
def dashboard():
    return jsonify(
        {
            "total_users": g.db.query(User).count(),
            "total_lots": g.db.query(ParkingLot).count(),
            "total_spots": g.db.query(ParkingSpot).count(),
            "available_spots": g.db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.AVAILABLE).count(),
            "active_reservations": g.db.query(Reservation)
            .filter(Reservation.status == ReservationStatus.ACTIVE)
            .count(),
        }
    )


@admin_bp.get("/users")
@admin_required
def list_users():
    users = g.db.query(User).order_by(User.created_at.desc()).all()
    return jsonify([user_to_dict(user) for user in users])


@admin_bp.patch("/users/<int:user_id>")
@admin_required
def update_user(user_id: int):
    user = g.db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ApiError("User not found", 404)

    data = request.get_json(silent=True) or {}
    if user.id == g.current_user.id and data.get("is_active") is False:
        raise ApiError("Cannot deactivate your own account", 400)

    if "full_name" in data:
        user.full_name = data["full_name"]
    if "is_active" in data:
        user.is_active = data["is_active"]
    if "role" in data:
        try:
            user.role = UserRole(data["role"])
        except ValueError as exc:
            raise ApiError(f"Invalid role: {data['role']}", 422) from exc

    g.db.commit()
    g.db.refresh(user)
    return jsonify(user_to_dict(user))


@admin_bp.post("/seed")
@admin_required
def seed_demo_data():
    if g.db.query(ParkingLot).count() > 0:
        raise ApiError("Data already seeded", 409)

    if not g.db.query(User).filter(User.role == UserRole.ADMIN).first():
        admin = User(
            email="admin@parksmart.com",
            hashed_password=hash_password("Admin123!"),
            full_name="System Admin",
            role=UserRole.ADMIN,
        )
        g.db.add(admin)

    lot = ParkingLot(
        name="Main Campus Lot",
        address="123 University Ave",
        description="Primary parking facility near the main entrance",
    )
    g.db.add(lot)
    g.db.flush()

    for i in range(1, 11):
        g.db.add(ParkingSpot(lot_id=lot.id, spot_number=f"A-{i:02d}"))

    lot2 = ParkingLot(
        name="Visitor Parking",
        address="456 Guest Blvd",
        description="Short-term visitor parking",
    )
    g.db.add(lot2)
    g.db.flush()

    for i in range(1, 6):
        g.db.add(ParkingSpot(lot_id=lot2.id, spot_number=f"V-{i:02d}"))

    g.db.commit()
    return jsonify({"message": "Demo data seeded successfully"}), 201
