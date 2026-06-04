from flask import Blueprint, g, jsonify, request

from app.decorators import admin_required, with_db
from app.errors import ApiError
from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot, SpotStatus, SpotType
from app.serializers import lot_to_dict, spot_to_dict

parking_bp = Blueprint("parking", __name__, url_prefix="/api/v1/parking")


@parking_bp.get("/lots")
@with_db
def list_lots():
    lots = g.db.query(ParkingLot).order_by(ParkingLot.name).all()
    return jsonify([lot_to_dict(lot) for lot in lots])


@parking_bp.post("/lots")
@admin_required
def create_lot():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("address"):
        raise ApiError("name and address are required", 422)

    lot = ParkingLot(name=data["name"], address=data["address"], description=data.get("description"))
    g.db.add(lot)
    g.db.commit()
    g.db.refresh(lot)
    return jsonify(lot_to_dict(lot)), 201


@parking_bp.get("/lots/<int:lot_id>")
@with_db
def get_lot(lot_id: int):
    lot = g.db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise ApiError("Parking lot not found", 404)
    return jsonify(lot_to_dict(lot))


@parking_bp.patch("/lots/<int:lot_id>")
@admin_required
def update_lot(lot_id: int):
    lot = g.db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise ApiError("Parking lot not found", 404)

    data = request.get_json(silent=True) or {}
    for field in ("name", "address", "description"):
        if field in data:
            setattr(lot, field, data[field])

    g.db.commit()
    g.db.refresh(lot)
    return jsonify(lot_to_dict(lot))


@parking_bp.get("/spots")
@with_db
def list_spots():
    query = g.db.query(ParkingSpot)

    lot_id = request.args.get("lot_id", type=int)
    status_filter = request.args.get("status")
    spot_type = request.args.get("spot_type")

    if lot_id is not None:
        query = query.filter(ParkingSpot.lot_id == lot_id)
    if status_filter is not None:
        try:
            query = query.filter(ParkingSpot.status == SpotStatus(status_filter))
        except ValueError as exc:
            raise ApiError(f"Invalid status: {status_filter}", 422) from exc
    if spot_type is not None:
        try:
            query = query.filter(ParkingSpot.spot_type == SpotType(spot_type))
        except ValueError as exc:
            raise ApiError(f"Invalid spot_type: {spot_type}", 422) from exc

    spots = query.order_by(ParkingSpot.lot_id, ParkingSpot.spot_number).all()
    return jsonify([spot_to_dict(spot) for spot in spots])


@parking_bp.post("/spots")
@admin_required
def create_spot():
    data = request.get_json(silent=True) or {}
    if not data.get("lot_id") or not data.get("spot_number"):
        raise ApiError("lot_id and spot_number are required", 422)

    lot = g.db.query(ParkingLot).filter(ParkingLot.id == data["lot_id"]).first()
    if not lot:
        raise ApiError("Parking lot not found", 404)

    spot_type = SpotType.STANDARD
    if data.get("spot_type"):
        try:
            spot_type = SpotType(data["spot_type"])
        except ValueError as exc:
            raise ApiError(f"Invalid spot_type: {data['spot_type']}", 422) from exc

    spot = ParkingSpot(lot_id=data["lot_id"], spot_number=data["spot_number"], spot_type=spot_type)
    g.db.add(spot)
    g.db.commit()
    g.db.refresh(spot)
    return jsonify(spot_to_dict(spot)), 201


@parking_bp.get("/spots/<int:spot_id>")
@with_db
def get_spot(spot_id: int):
    spot = g.db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise ApiError("Parking spot not found", 404)
    return jsonify(spot_to_dict(spot))


@parking_bp.patch("/spots/<int:spot_id>")
@admin_required
def update_spot(spot_id: int):
    spot = g.db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise ApiError("Parking spot not found", 404)

    data = request.get_json(silent=True) or {}
    if "spot_number" in data:
        spot.spot_number = data["spot_number"]
    if "status" in data:
        try:
            spot.status = SpotStatus(data["status"])
        except ValueError as exc:
            raise ApiError(f"Invalid status: {data['status']}", 422) from exc
    if "spot_type" in data:
        try:
            spot.spot_type = SpotType(data["spot_type"])
        except ValueError as exc:
            raise ApiError(f"Invalid spot_type: {data['spot_type']}", 422) from exc

    g.db.commit()
    g.db.refresh(spot)
    return jsonify(spot_to_dict(spot))
