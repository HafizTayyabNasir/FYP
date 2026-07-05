from pydantic import BaseModel
from app.schemas.user import User

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str | None = None
    
class Login(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    token: str
    user: User
