from pydantic import BaseModel

class SignupSchema(BaseModel):
    username: str
    email: str
    password: str | int


class LoginSchema(BaseModel):
    email: str
    password: str | int

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class RefreshSchema(BaseModel):
    refresh_token: str