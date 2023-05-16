import amanuensis
from amanuensis.models import AssociatedUser

__all__ = [
    "update_associated_users",
    "update_associated_user",
    "get_associated_users",
    "get_associated_user_by_id",
    "get_associated_users_by_id",
    "get_associated_user_by_user_id",
    
]


def get_associated_users(current_session, emails):
    if not emails:
        return []
    return (
        current_session.query(AssociatedUser)
        .filter(AssociatedUser.email.in_(emails))
        .all()
    )


def get_associated_user_by_id(current_session, id):
    if not id:
        return
    return (
        current_session.query(AssociatedUser).filter(AssociatedUser.id==id).first()
    )

def get_associated_users_by_id(current_session, ids):
    if not ids:
        return []
    return (
        current_session.query(AssociatedUser)
        .filter(AssociatedUser.user_id.in_(ids))
        .all()
    )

def get_associated_user_by_user_id(current_session, id):
    if not id:
        return
    return (
        current_session.query(AssociatedUser)
        .filter(AssociatedUser.user_id == id)
        .first()
    )

def update_associated_user(current_session, associated_user):

    user = get_associated_user_by_id(
        current_session=current_session, id=associated_user.id
    )
    if not user:
        raise amanuensis.errors.NotFound("Associated user not found.")
    
    user.email = associated_user.email
    user.user_id = associated_user.user_id

    current_session.flush()

    return "200"


def update_associated_users(current_session, associated_users):

    for user in associated_users:
        update_associated_user(
            current_session=current_session, associated_user=user
        )

    return "200"
