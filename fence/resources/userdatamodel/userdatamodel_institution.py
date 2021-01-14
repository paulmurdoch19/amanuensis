from sqlalchemy import func

from fence.errors import NotFound, UserError
from fence.models import (
    Institution,
)

__all__ = [
	"get_institution",
	"get_all_institutions",
    "update_institution",
    "add_institution",
]

def get_institution(current_session, uid):
    return current_session.query(Institution).filter_by(uid=uid).first()

def get_all_institutions(current_session):
    institutions = current_session.query(Institution).all()
    return {"institutions": institutions}

def update_institution(current_session, uid, display_name):
    return (
        current_session.query(Institution).filter(Institution.uid == uid).update({Institution.display_name: display_name})
    )

def add_institution(current_session, display_name, uid):
    """
    Creates an institution
    """
    new_institution = Institution(display_name=display_name, uid=uid)

    current_session.add(new_institution)
    current_session.flush()
    return new_institution