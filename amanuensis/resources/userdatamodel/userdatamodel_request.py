from sqlalchemy import func


from amanuensis.errors import NotFound, UserError
from amanuensis.models import (
    Request,
    Project
)

__all__ = [
    "get_requests",
    "get_request_by_id",
    "get_request_by_consortium",
]


def get_requests(current_session, user_id):
    return current_session.query(Request).join(Request.project).filter_by(user_id=user_id).all()

def get_request_by_consortium(current_session, user_id, consortium):
    return current_session.query(Request).join(Request.consortium_data_contributor).filter_by(code=consortium).all()

def get_request_by_id(current_session, user_id, request_id):
    return current_session.query(Request).filter_by(id=request_id).join(Request.project).filter_by(user_id=user_id).first()

