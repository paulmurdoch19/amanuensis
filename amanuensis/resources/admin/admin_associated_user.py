from collections import defaultdict

import flask
from cdislogging import get_logger

from amanuensis.config import config
from amanuensis.errors import UserError
from amanuensis.resources import fence
from amanuensis.resources import userdatamodel as udm
from amanuensis.schema import AssociatedUserSchema

logger = get_logger(__name__)

__all__ = [
    "update_role",
    "add_associated_users",
]


def update_role(project_id, user_id, email, role):
    with flask.current_app.db.session as session:
        ret = udm.update_associated_users(session, project_id, user_id, email, role)
        return ret


def add_associated_users(users):

    users = [defaultdict(lambda: "", user) for user in users]

    with flask.current_app.db.session as session:
        associated_user_schema = AssociatedUserSchema(many=True)
        ret = []
        users_with_id, users_with_email = [], []
        for user in users:
            if "email" in user:
                users_with_email.append(user)
            elif "id" in user:
                users_with_id.append(user)
            else:
                raise UserError(
                    "The associated user must have at least an email or id. Neither was found."
                )
        user_emails = [user["email"] for user in users_with_email]
        user_ids = [user["id"] for user in users_with_id]

        associated_users = udm.get_associated_users(session, user_emails)
        associated_users += udm.get_associated_users_by_id(session, user_ids)

        fence_users = []
        if user_emails:
            fence_users.extend(
                fence.fence_get_users(config, usernames=user_emails)["users"]
            )
        if user_ids:
            fence_users.extend(fence.fence_get_users(config, ids=user_ids)["users"])
        if fence_users:
            fence_users = [
                {"email": user["name"], "id": user["id"]} for user in fence_users
            ]

        user_missing = []  # users not found in associated users table

        associated_user_emails = [a_user.email for a_user in associated_users]

        for user in users_with_email:
            if user["email"] not in associated_user_emails:
                user_missing.append(user)

        associated_user_ids = [a_user.user_id for a_user in associated_users]

        for user in users_with_id:
            if user["id"] not in associated_user_ids:
                user_missing.append(user)

        # Check against fence and use fence as an authoritative source.
        for user in associated_users:
            for fence_user in fence_users:
                if (
                    user.email == fence_user["email"]
                    and user.user_id != fence_user["id"]
                ):
                    user.user_id = fence_user["id"]
                    udm.associate_user.update_associated_user(session, user)
                elif (
                    user.email != fence_user["email"]
                    and user.user_id == fence_user["id"]
                ):
                    user.email = fence_user["email"]
                    udm.associate_user.update_associated_user(session, user)

        for user in user_missing:
            for fence_user in fence_users:
                if (
                    user["email"] == fence_user["email"]
                    and user["id"] != fence_user["id"]
                ):
                    user["id"] = fence_user["id"]
                elif (
                    user["email"] != fence_user["email"]
                    and user["id"] == fence_user["id"]
                ):
                    user["email"] = fence_user["email"]

            ret.append(
                udm.add_associated_user(
                    session,
                    project_id=user["project_id"],
                    email=user["email"],
                    user_id=user["id"],
                )
            )

        associated_user_schema.dump(ret)
        return ret
