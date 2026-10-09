from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """
    Request schema for creating a user.
    Replaces the Java record UserCreateRequest with Jakarta Validation annotations.
    Pydantic handles the same validation rules natively.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username is required",
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Email must be valid",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="Password is required",
    )


class UserResponse(BaseModel):
    """
    Response schema for user data.
    Replaces the Java record UserResponse.
    """

    id: UUID
    username: str
    email: str
    enabled: bool

    model_config = {"from_attributes": True}
