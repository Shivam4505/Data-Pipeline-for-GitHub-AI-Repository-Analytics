# GitHub AI Repository Analytics - Common API Models
from datetime import date, datetime
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, field_validator


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class DateRangeParams(BaseModel):
    """Date range parameters."""
    start_date: Optional[date] = Field(default=None, description="Start date (inclusive)")
    end_date: Optional[date] = Field(default=None, description="End date (inclusive)")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "PaginatedResponse[T]":
        total_pages = (total + params.per_page - 1) // params.per_page
        return cls(
            items=items,
            total=total,
            page=params.page,
            per_page=params.per_page,
            total_pages=total_pages,
        )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = "unknown"
    cache: str = "unknown"