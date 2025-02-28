from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List


class UserBase(BaseModel):
    username: str = Field(..., example="user123")
    full_name: Optional[str] = Field(None, example="User Name")
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePassword123")


class UserCreateRequest(UserBase):
    # Model for user creation.
    password: str = Field(..., example="SecurePassword123")


class UserResponse(BaseModel):
    # Model for returning user data (excluding sensitive fields).
    user_id: str = Field(..., example="60f8b43e4e92b2b1f8a0c7a5")
    username: str = Field(..., example="user123")
    email: EmailStr = Field(..., example="user@example.com")
    full_name: Optional[str] = Field(None, example="User Name")
    premium:Optional[bool]=Field(default=False)

    # Update for Pydantic v2
    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    # Model for login requests.
    username: str = Field(..., example="user123")
    password: str = Field(..., example="SecurePassword123")


class TokenResponse(BaseModel):
    # Model for token responses.
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1...")  # Added refresh token
    token_type: str = Field(..., example="bearer")


class TokenData(BaseModel):
    # Model for token payload data.
    username: Optional[str] = Field(None, example="user123")
    exp: Optional[int] = Field(None, description="Token expiry timestamp")


class UserUpdateRequest(BaseModel):
    # Model for updating user details.
    full_name: Optional[str] = Field(None, example="Updated User Name")
    email: Optional[EmailStr] = Field(None, example="updated_email@example.com")
    password: Optional[str] = Field(None, example="NewSecurePassword123")


class UserListResponse(BaseModel):
    # Model for listing multiple users.
    users: List[UserResponse]
