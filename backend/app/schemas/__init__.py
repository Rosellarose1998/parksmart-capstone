from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.parking_spot import SpotStatus, SpotType
from app.models.reservation import ReservationStatus
from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None
    role: UserRole | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: int | None = None


class ParkingLotCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    description: str | None = None


class ParkingLotUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None


class ParkingLotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    description: str | None
    created_at: datetime


class ParkingSpotCreate(BaseModel):
    lot_id: int
    spot_number: str = Field(min_length=1, max_length=50)
    spot_type: SpotType = SpotType.STANDARD


class ParkingSpotUpdate(BaseModel):
    spot_number: str | None = Field(default=None, min_length=1, max_length=50)
    status: SpotStatus | None = None
    spot_type: SpotType | None = None


class ParkingSpotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    spot_number: str
    status: SpotStatus
    spot_type: SpotType
    created_at: datetime


class ReservationCreate(BaseModel):
    spot_id: int
    start_time: datetime
    end_time: datetime


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    spot_id: int
    start_time: datetime
    end_time: datetime
    status: ReservationStatus
    created_at: datetime


class ReservationDetailResponse(ReservationResponse):
    spot: ParkingSpotResponse | None = None
    user: UserResponse | None = None


class DashboardStats(BaseModel):
    total_users: int
    total_lots: int
    total_spots: int
    available_spots: int
    active_reservations: int
