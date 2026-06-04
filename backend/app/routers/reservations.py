from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User
from app.schemas import ReservationCreate, ReservationDetailResponse, ReservationResponse
from app.services.reservation import cancel_reservation, create_reservation

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create(data: ReservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_reservation(db, current_user.id, data)


@router.get("/me", response_model=list[ReservationDetailResponse])
def list_my_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reservations = (
        db.query(Reservation)
        .options(joinedload(Reservation.spot), joinedload(Reservation.user))
        .filter(Reservation.user_id == current_user.id)
        .order_by(Reservation.start_time.desc())
        .all()
    )
    return reservations


@router.get("", response_model=list[ReservationDetailResponse])
def list_all_reservations(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return (
        db.query(Reservation)
        .options(joinedload(Reservation.spot), joinedload(Reservation.user))
        .order_by(Reservation.created_at.desc())
        .all()
    )


@router.get("/{reservation_id}", response_model=ReservationDetailResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = (
        db.query(Reservation)
        .options(joinedload(Reservation.spot), joinedload(Reservation.user))
        .filter(Reservation.id == reservation_id)
        .first()
    )
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    if reservation.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return reservation


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
def cancel(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    if reservation.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return cancel_reservation(db, reservation)
