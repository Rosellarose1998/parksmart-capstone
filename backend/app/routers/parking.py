from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_admin
from app.models.parking_lot import ParkingLot
from app.models.parking_spot import ParkingSpot, SpotStatus, SpotType
from app.schemas import (
    ParkingLotCreate,
    ParkingLotResponse,
    ParkingLotUpdate,
    ParkingSpotCreate,
    ParkingSpotResponse,
    ParkingSpotUpdate,
)

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.get("/lots", response_model=list[ParkingLotResponse])
def list_lots(db: Session = Depends(get_db)):
    return db.query(ParkingLot).order_by(ParkingLot.name).all()


@router.post("/lots", response_model=ParkingLotResponse, status_code=status.HTTP_201_CREATED)
def create_lot(data: ParkingLotCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    lot = ParkingLot(**data.model_dump())
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@router.get("/lots/{lot_id}", response_model=ParkingLotResponse)
def get_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")
    return lot


@router.patch("/lots/{lot_id}", response_model=ParkingLotResponse)
def update_lot(
    lot_id: int,
    data: ParkingLotUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lot, field, value)
    db.commit()
    db.refresh(lot)
    return lot


@router.get("/spots", response_model=list[ParkingSpotResponse])
def list_spots(
    lot_id: int | None = Query(default=None),
    status_filter: SpotStatus | None = Query(default=None, alias="status"),
    spot_type: SpotType | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(ParkingSpot)
    if lot_id is not None:
        query = query.filter(ParkingSpot.lot_id == lot_id)
    if status_filter is not None:
        query = query.filter(ParkingSpot.status == status_filter)
    if spot_type is not None:
        query = query.filter(ParkingSpot.spot_type == spot_type)
    return query.order_by(ParkingSpot.lot_id, ParkingSpot.spot_number).all()


@router.post("/spots", response_model=ParkingSpotResponse, status_code=status.HTTP_201_CREATED)
def create_spot(data: ParkingSpotCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == data.lot_id).first()
    if not lot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking lot not found")

    spot = ParkingSpot(**data.model_dump())
    db.add(spot)
    db.commit()
    db.refresh(spot)
    return spot


@router.get("/spots/{spot_id}", response_model=ParkingSpotResponse)
def get_spot(spot_id: int, db: Session = Depends(get_db)):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking spot not found")
    return spot


@router.patch("/spots/{spot_id}", response_model=ParkingSpotResponse)
def update_spot(
    spot_id: int,
    data: ParkingSpotUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking spot not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(spot, field, value)
    db.commit()
    db.refresh(spot)
    return spot
