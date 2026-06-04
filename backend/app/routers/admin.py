from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot, SpotStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User, UserRole
from app.schemas import DashboardStats, UserResponse, UserUpdate
from app.utils.auth import hash_password

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return DashboardStats(
        total_users=db.query(User).count(),
        total_lots=db.query(ParkingLot).count(),
        total_spots=db.query(ParkingSpot).count(),
        available_spots=db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.AVAILABLE).count(),
        active_reservations=db.query(Reservation).filter(Reservation.status == ReservationStatus.ACTIVE).count(),
    )


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id and data.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.post("/seed", status_code=status.HTTP_201_CREATED)
def seed_demo_data(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Seed demo parking lots and spots for development/demo purposes."""
    if db.query(ParkingLot).count() > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Data already seeded")

    if not db.query(User).filter(User.role == UserRole.ADMIN).first():
        admin = User(
            email="admin@parksmart.com",
            hashed_password=hash_password("Admin123!"),
            full_name="System Admin",
            role=UserRole.ADMIN,
        )
        db.add(admin)

    lot = ParkingLot(
        name="Main Campus Lot",
        address="123 University Ave",
        description="Primary parking facility near the main entrance",
    )
    db.add(lot)
    db.flush()

    for i in range(1, 11):
        db.add(ParkingSpot(lot_id=lot.id, spot_number=f"A-{i:02d}"))

    lot2 = ParkingLot(
        name="Visitor Parking",
        address="456 Guest Blvd",
        description="Short-term visitor parking",
    )
    db.add(lot2)
    db.flush()

    for i in range(1, 6):
        db.add(ParkingSpot(lot_id=lot2.id, spot_number=f"V-{i:02d}"))

    db.commit()
    return {"message": "Demo data seeded successfully"}
