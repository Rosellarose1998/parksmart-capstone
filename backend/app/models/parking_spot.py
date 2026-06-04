import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SpotStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


class SpotType(str, enum.Enum):
    STANDARD = "standard"
    COMPACT = "compact"
    HANDICAP = "handicap"
    EV = "ev"


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lot_id: Mapped[int] = mapped_column(ForeignKey("parking_lots.id", ondelete="CASCADE"), nullable=False)
    spot_number: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[SpotStatus] = mapped_column(Enum(SpotStatus), default=SpotStatus.AVAILABLE, nullable=False)
    spot_type: Mapped[SpotType] = mapped_column(Enum(SpotType), default=SpotType.STANDARD, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lot = relationship("ParkingLot", back_populates="spots")
    reservations = relationship("Reservation", back_populates="spot", cascade="all, delete-orphan")
