from collections import defaultdict

import flask
from cdislogging import get_logger

from amanuensis.config import config
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

    users = [defaultdict(lambda: None, user) for user in users]

    with flask.current_app.db.session as session:
        associated_user_schema = AssociatedUserSchema(many=True)
        ret = []
        user_emails = [user["email"] for user in users]
        user_ids = [user["id"] for user in users]

        fence_users_by_email = fence.fence_get_users(config, usernames=user_emails)[
            "users"
        ]
        fence_users_by_id = fence.fence_get_users(config, ids=user_ids)["users"]

        fence_users, seen_emails = [], []
        all_fence_users = fence_users_by_email + fence_users_by_id
        for user in all_fence_users:
            if user["name"] not in seen_emails:
                seen_emails.append(user["name"])
                fence_users.append(
                    {
                        "id": user["id"],
                        "name": user["name"],
                    }
                )

        verified_users, new_users = [], []
        for user in users:
            in_fence = False
            for fence_user in fence_users:
                if user["email"] == fence_user["name"]:
                    user["id"] = fence_user["id"]
                    verified_users.append(user)
                    in_fence = True
                elif user["id"] == fence_user["id"]:
                    user["email"] = fence_user["name"]
                    verified_users.append(user)
                    in_fence = True
            if (
                not in_fence and user["email"]
            ):  # if the user is not in fence having only user_id is meaningless.
                new_users.append(user)

        all_users = verified_users + new_users
        user_emails = [user["email"] for user in all_users]
        user_ids = [user["id"] for user in verified_users]

        associated_users = udm.get_associated_users(session, user_emails)

        associated_users_by_id = udm.get_associated_users_by_id(session, user_ids)

        for user in associated_users_by_id:
            if user not in associated_users:
                associated_users.append(user)

        # Check associated_user against fence and use fence as an authoritative source.
        for associated_user in associated_users:
            for verified_user in verified_users:
                if (
                    associated_user.email == verified_user["email"]
                    and associated_user.user_id != verified_user["id"]
                ):
                    associated_user.user_id = verified_user["id"]
                    udm.associate_user.update_associated_user(session, associated_user)

                elif (
                    associated_user.email != verified_user["email"]
                    and associated_user.user_id == verified_user["id"]
                ):

                    associated_user.email = verified_user["email"]
                    udm.associate_user.update_associated_user(
                        session, associated_user=associated_user
                    )

        for associated_user in associated_users:
            projects = [project.id for project in associated_user.projects]
            for user in all_users:
                if user["email"] == associated_user.email:
                    project_id = user["project_id"]
                    if project_id not in projects:
                        ret.append(
                            udm.add_associated_user_to_project(
                                session,
                                associated_user=associated_user,
                                project_id=project_id,
                            )
                        )

        associated_user_emails = [user.email for user in associated_users]

        for user in all_users:
            if user["email"] not in associated_user_emails:
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
