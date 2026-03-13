"""Password hasher adapter. Implements core.ports.password_hasher.PasswordHasher using bcrypt."""
import bcrypt

from core.ports.password_hasher import PasswordHasher as PasswordHasherPort


class PasswordHasherImpl(PasswordHasherPort):
    """Bcrypt implementation of PasswordHasher port."""

    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
