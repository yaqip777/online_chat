from pydantic import BaseModel, field_validator


class SignupSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned.endswith("@gmail.com"):
            raise ValueError("Email @gmail.com bilan tugashi shart!")
        return cleaned

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 3:
            raise ValueError("Username kamida 3 ta belgidan iborat bo'lishi kerak!")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Parol kamida 6 ta belgidan iborat bo'lishi kerak!")
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "yaqip",
                    "first_name": "Yaqip",
                    "last_name": "Joldasbaev",
                    "email": "user@gmail.com",
                    "password": "secretpassword",
                }
            ]
        }
    }


class LoginSchema(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.strip().lower()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@gmail.com",
                    "password": "secretpassword",
                }
            ]
        }
    }


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshSchema(BaseModel):
    refresh_token: str
