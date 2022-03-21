import re
import time
from urllib.parse import urlparse

from cached_property import cached_property
import cirrus
from cirrus import GoogleCloudManager
from cdislogging import get_logger
from cdispyutils.config import get_value
from cdispyutils.hmac4 import generate_aws_presigned_url
import flask
import requests

from amanuensis.auth import (
    get_jwt,
    has_oauth,
    current_token,
    login_required,
    set_current_token,
    validate_request,
    JWTError,
)
from amanuensis.config import config
from amanuensis.errors import (
    InternalError,
    NotFound,
    NotSupported,
    Unauthorized,
    UnavailableError,
)
from amanuensis.resources.google.utils import (
    get_or_create_primary_service_account_key,
    create_primary_service_account_key,
    get_or_create_proxy_group_id,
    get_google_app_creds,
    give_service_account_billing_access_if_necessary,
)
from amanuensis.utils import get_valid_expiration_from_request
from . import multipart_upload


logger = get_logger(__name__)

ACTION_DICT = {
    "s3": {"upload": "PUT", "download": "GET"},
    "gs": {"upload": "PUT", "download": "GET"},
}

SUPPORTED_PROTOCOLS = ["s3", "http", "ftp", "https", "gs"]
SUPPORTED_ACTIONS = ["upload", "download"]
ANONYMOUS_USER_ID = "anonymous"
ANONYMOUS_USERNAME = "anonymous"


def get_signed_url_for_file(action, file_id, file_name=None):
    requested_protocol = flask.request.args.get("protocol", None)
    r_pays_project = flask.request.args.get("userProject", None)

    # default to signing the url even if it's a public object
    # this will work so long as we're provided a user token
    force_signed_url = True
    if flask.request.args.get("no_force_sign"):
        force_signed_url = False

    indexed_file = IndexedFile(file_id)
    expires_in = 3600
    requested_expires_in = get_valid_expiration_from_request()
    if requested_expires_in:
        expires_in = min(requested_expires_in, expires_in)

    signed_url = indexed_file.get_signed_url(
        requested_protocol,
        action,
        expires_in,
        force_signed_url=force_signed_url,
        r_pays_project=r_pays_project,
        file_name=file_name,
    )
    return {"url": signed_url}




def _get_user_info():
    """
    Attempt to parse the request for token to authenticate the user. fallback to
    populated information about an anonymous user.
    """
    try:
        set_current_token(validate_request(aud={"user"}))
        user_id = str(current_token["sub"])
        username = current_token["context"]["user"]["name"]
    except JWTError:
        # this is fine b/c it might be public data, sign with anonymous username/id
        user_id = ANONYMOUS_USER_ID
        username = ANONYMOUS_USERNAME

    return {"user_id": user_id, "username": username}


def _is_anonymous_user(user_info):
    """
    Check if there's a current user authenticated or if request is anonymous
    """
    user_info = user_info or _get_user_info()
    return user_info.get("user_id") == ANONYMOUS_USER_ID


def filter_auth_ids(action, list_auth_ids):
    checked_permission = ""
    if action == "download":
        checked_permission = "read-storage"
    elif action == "upload":
        checked_permission = "write-storage"
    authorized_dbgaps = []
    for key, values in list(list_auth_ids.items()):
        if checked_permission in values:
            authorized_dbgaps.append(key)
    return authorized_dbgaps
