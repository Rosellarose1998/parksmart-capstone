from datetime import UTC, datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.errors import ApiError
from app.models.parking_spot import ParkingSpot, SpotStatus
from app.models.reservation import Reservation, ReservationStatus


def validate_reservation_times(start_time: datetime, end_time: datetime) -> None:
    now = datetime.now(UTC)
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=UTC)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=UTC)

    if start_time >= end_time:
        raise ApiError("End time must be after start time", 400)
    if start_time < now:
        raise ApiError("Start time must be in the future", 400)


def check_spot_availability(db: Session, spot_id: int, start_time: datetime, end_time: datetime) -> ParkingSpot:
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise ApiError("Parking spot not found", 404)
    if spot.status in (SpotStatus.OCCUPIED, SpotStatus.MAINTENANCE):
        raise ApiError(f"Spot is {spot.status.value}", 409)

    overlapping = (
        db.query(Reservation)
        .filter(
            Reservation.spot_id == spot_id,
            Reservation.status == ReservationStatus.ACTIVE,
            or_(
                and_(Reservation.start_time <= start_time, Reservation.end_time > start_time),
                and_(Reservation.start_time < end_time, Reservation.end_time >= end_time),
                and_(Reservation.start_time >= start_time, Reservation.end_time <= end_time),
            ),
        )
        .first()
    )
    if overlapping:
        raise ApiError("Spot is already reserved for this time slot", 409)
    return spot


def create_reservation(
    db: Session,
    user_id: int,
    *,
    spot_id: int,
    start_time: datetime,
    end_time: datetime,
) -> Reservation:
    validate_reservation_times(start_time, end_time)
    spot = check_spot_availability(db, spot_id, start_time, end_time)

    reservation = Reservation(
        user_id=user_id,
        spot_id=spot_id,
        start_time=start_time,
        end_time=end_time,
        status=ReservationStatus.ACTIVE,
    )
    spot.status = SpotStatus.RESERVED
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation: Reservation) -> Reservation:
    if reservation.status != ReservationStatus.ACTIVE:
        raise ApiError("Only active reservations can be cancelled", 400)

    reservation.status = ReservationStatus.CANCELLED
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == reservation.spot_id).first()
    if spot:
        active_count = (
            db.query(Reservation)
            .filter(
                Reservation.spot_id == spot.id,
                Reservation.status == ReservationStatus.ACTIVE,
                Reservation.id != reservation.id,
            )
            .count()
        )
        if active_count == 0:
            spot.status = SpotStatus.AVAILABLE

    db.commit()
    db.refresh(reservation)
    return reservation
