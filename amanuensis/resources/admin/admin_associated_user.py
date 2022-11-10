import flask
from cdislogging import get_logger

from amanuensis.config import config
from amanuensis.resources import fence
from amanuensis.resources import userdatamodel as udm
from amanuensis.schema import (
    AssociatedUserSchema,
    ConsortiumDataContributorSchema,
    RequestSchema,
    StateSchema,
)
from amanuensis.errors import UserError

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
    with flask.current_app.db.session as session:
        associated_user_schema = AssociatedUserSchema(many=True)
        ret = []
        users_with_email = [user for user in users if "email" in user]
        users_with_id = [
            user
            for user in users
            if "id" in user
        ]
        user_emails = [user["email"] for user in users_with_email]
        user_ids = [user["id"] for user in users_with_id]
        associated_users = udm.get_associated_users(session, user_emails)
        associated_users += udm.get_associated_users_by_id(session, user_ids)

        associated_user_emails = [user.email for user in associated_users]
        associated_user_ids = [user.user_id for user in associated_users]


        user_emails = [user["email"] for user in users_with_email]
        user_ids = [user["id"] for user in users_with_id]

        fence_users = []
        if user_emails:
            fence_users.extend(fence.fence_get_users(config, usernames=user_emails)["users"])
        if user_ids:
            fence_users.extend(fence.fence_get_users(config, ids=user_ids)["users"])
        if fence_users:
            fence_users = [
                {"email": user["name"], "id": user["id"]} for user in fence_users
            ]

        for fence_user in fence_users:
            for user in users_with_email:
                if user["email"] == fence_user["email"]:
                    user["id"] = fence_user["id"]
                    break

        for fence_user in fence_users:
            for user in users_with_id:
                if user["id"] == fence_user["id"]:
                    user["email"] = fence_user["email"]
                    break
        
        users.clear()
        users = users_with_email + users_with_id
        seen_id, seen_email = associated_user_ids, associated_user_emails
        for user in users:
            email, user_id = None, None
            if "email" in user:
                if user["email"] not in seen_email:
                    seen_email.append(user["email"])
                    email = user["email"]
                else:
                    continue
            if "id" in user:
                if user["id"] not in seen_id:
                    seen_id.append(user["id"])
                    user_id = user["id"]
                else:
                    continue
            if not (user_id or email):
                raise UserError("The associated user must have at least an email or id. Neither was found.")

            ret.append(
                udm.add_associated_user(
                    session,
                    user["project_id"],
                    email,
                    user_id,
                )
            )
        associated_user_schema.dump(ret)
        return ret
