from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    JUDGED = "judged"
    FAILED = "failed"
