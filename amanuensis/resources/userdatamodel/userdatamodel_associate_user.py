import amanuensis
from amanuensis.models import AssociatedUser

__all__ = [
    "update_associated_users",
    "update_associated_user",
    "get_associated_users",
    "get_associated_user_by_id",
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
        current_session.query(AssociatedUser).filter(AssociatedUser.id.in_(id)).first()
    )


def update_associated_user(current_session, associated_user):

    user = get_associated_user_by_id(
        current_session=current_session, id=associated_user.id
    )
    logger.error(f"user: {type(user)}")
    logger.error(f"associated_user: {type(associated_user)}")
    user.email = associated_user.email
    user.user_id = associated_user.user_id

    current_session.flush()

    return "200"


def update_associated_users(current_session, associated_users):

    for user in associated_users:
        update_associated_user(
            current_session=current_session, id=user.user_id, email=user.email
        )

    return "200"
