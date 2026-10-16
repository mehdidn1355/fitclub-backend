from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """رمز عبور رو hash می‌کنه."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """بررسی می‌کنه که رمز عبور با hash مطابقت داره یا نه."""
    return pwd_context.verify(plain_password, hashed_password)