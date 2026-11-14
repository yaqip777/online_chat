import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.models import User
from backend.auth.schemes.post import LoginSchema, SignupSchema
from backend.config import settings
from backend.database import get_db

bearer_scheme = HTTPBearer()
optional_bearer_scheme = HTTPBearer(auto_error=False)


class AuthService:
    @staticmethod
    async def sign_up(data: SignupSchema, db: AsyncSession):
        existing_user = await db.execute(
            select(User).where(
                or_(User.email == data.email, User.username == data.username)
            )
        )
        found = existing_user.scalar_one_or_none()
        if found is not None:
            if found.email == data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu email allaqachon ro'yxatdan o'tgan",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu username allaqachon band qilingan",
                )

        user = User(
            username=data.username,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password=AuthService.get_password_hash(data.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        tokens = {
            "access_token": AuthService.create_access_token({"email": user.email, "user_id": user.id}),
            "refresh_token": AuthService.create_refresh_token({"email": user.email, "user_id": user.id}),
            "token_type": "bearer",
        }
        return {"message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi", "tokens": tokens}

    @staticmethod
    async def login(data: LoginSchema, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if user is None or not AuthService.verify_password(data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email yoki parol noto'g'ri",
            )

        tokens = {
            "access_token": AuthService.create_access_token({"email": user.email, "user_id": user.id}),
            "refresh_token": AuthService.create_refresh_token({"email": user.email, "user_id": user.id}),
            "token_type": "bearer",
        }
        return {"message": "Tizimga kirish muvaffaqiyatli", "tokens": tokens}

    @staticmethod
    def get_password_hash(password: str) -> str:
        # bcrypt 72 byte limitini hisobga olgan holda
        pw_bytes = password.encode("utf-8")[:72]
        return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        pw_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> dict:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token yaroqsiz yoki muddati o'tgan",
        )
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email = payload.get("email")
            if email is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception

        new_access_token = AuthService.create_access_token({"email": user.email, "user_id": user.id})
        return {"access_token": new_access_token, "token_type": "bearer"}

    @staticmethod
    async def update_profile_picture(db: AsyncSession, user: User, image: UploadFile) -> User:
        if not image or not image.filename:
            raise HTTPException(status_code=400, detail="Rasm fayli tanlanmadi")

        file_ext = os.path.splitext(image.filename)[1].lower()
        if file_ext not in settings.IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Faqat quyidagi rasm formatlari qabul qilinadi: {', '.join(settings.IMAGE_EXTENSIONS)}",
            )

        content = await image.read()
        if len(content) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Rasm hajmi {settings.MAX_IMAGE_SIZE // (1024 * 1024)} MB dan oshmasligi kerak!",
            )
        await image.seek(0)

        # Eski profil rasmini o'chirish (agar mavjud bo'lsa)
        if user.profile_picture:
            old_path = settings.UPLOAD_DIR / user.profile_picture
            if old_path.exists() and old_path.is_file():
                try:
                    old_path.unlink()
                except OSError:
                    pass

        safe_filename = f"avatar_{user.id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}{file_ext}"
        target_path = settings.UPLOAD_DIR / safe_filename

        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        user.profile_picture = safe_filename
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiyadan o'tilmagan",
        )
        try:
            payload = jwt.decode(
                credentials.credentials, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email = payload.get("email")
            if email is None:
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception

        return user

    @staticmethod
    async def get_current_user_optional(
        credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User | None:
        if credentials is None:
            return None
        try:
            payload = jwt.decode(
                credentials.credentials, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email = payload.get("email")
            if email is None:
                return None
        except jwt.PyJWTError:
            return None

        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
