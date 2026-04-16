from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Ensure model metadata is registered for Alembic autogenerate.
from app.db.models.problem import Problem  # noqa: E402,F401
from app.db.models.submission import Submission  # noqa: E402,F401
from app.db.models.test_case import TestCase  # noqa: E402,F401
from app.db.models.user import User  # noqa: E402,F401
