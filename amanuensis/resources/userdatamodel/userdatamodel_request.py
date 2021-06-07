from sqlalchemy import func


from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    Request,
    Project
)

__all__ = [
    "get_requests",
]


def get_requests(current_session, user_id, consortium):
    return current_session.query(Request).join(Request.project).filter_by(user_id=user_id).all()


