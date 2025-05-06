from pydantic import BaseModel, EmailStr, constr, Field

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to send reset instructions to")

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token from email link")
    new_password: constr(min_length=8) = Field(..., description="New password must be at least 8 characters long")

class LogoutRequest(BaseModel):
    authorization: str = Field(..., description="Bearer token string to invalidate session")

class MessageResponse(BaseModel):
    message: str
    success: bool = True 