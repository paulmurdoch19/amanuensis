import os
import json
from boto.s3.connection import OrdinaryCallingFormat


DB = "postgresql://test:test@localhost:5432/amanuensis"

MOCK_AUTH = False
MOCK_STORAGE = False

SERVER_NAME = "http://localhost/user"
BASE_URL = SERVER_NAME
APPLICATION_ROOT = "/user"

ROOT_DIR = "/amanuensis"

# If using multi-tenant setup, configure this to the base URL for the provider
# amanuensis (i.e. ``BASE_URL`` in the provider amanuensis config).
# OIDC_ISSUER = 'http://localhost:8080/user

EMAIL_SERVER = "localhost"

SEND_FROM = "phillis.tt@gmail.com"

SEND_TO = "phillis.tt@gmail.com"

HMAC_ENCRYPTION_KEY = ""



"""
If the api is behind firewall that need to set http proxy:
    HTTP_PROXY = {'host': 'cloud-proxy', 'port': 3128}
"""
HTTP_PROXY = None
STORAGES = ["/cleversafe"]




SESSION_COOKIE_SECURE = False
ENABLE_CSRF_PROTECTION = True

INDEXD = "/index"

INDEXD_AUTH = ("gdcapi", "")

ARBORIST = "/rbac"

AWS_CREDENTIALS = {
    "CRED1": {"aws_access_key_id": "", "aws_secret_access_key": ""},
    "CRED2": {"aws_access_key_id": "", "aws_secret_access_key": ""},
}

ASSUMED_ROLES = {"arn:aws:iam::role1": "CRED1"}

DATA_UPLOAD_BUCKET = "bucket1"

S3_BUCKETS = {
    "bucket1": {"cred": "CRED1"},
    "bucket2": {"cred": "CRED2"},
    "bucket3": {"cred": "CRED1", "role-arn": "arn:aws:iam::role1"},
}


APP_NAME = ""



dir_path = "/secrets"
fence_creds = os.path.join(dir_path, "fence_credentials.json")



REMOVE_SERVICE_ACCOUNT_EMAIL_NOTIFICATION = {
    "enable": False,
    "domain": "smtp domain",
    "subject": "User service account removal notification",
    "from": "do-not-reply@planx-pla.net",
    "admin": [],
    "contact number": "123456789",
    "content": """
    The service accounts were removed from access control data because some \
users or service accounts of GCP project {} are not authorized to access \
the data sets associated to the service accounts, or do not \
adhere to the security policies.
    """,
}

SUPPORT_EMAIL_FOR_ERRORS = None
dbGaP = {}
if os.path.exists(fence_creds):
    with open(fence_creds, "r") as f:
        data = json.load(f)
        AWS_CREDENTIALS = data["AWS_CREDENTIALS"]
        S3_BUCKETS = data["S3_BUCKETS"]
        OIDC_ISSUER = data["OIDC_ISSUER"]
        APP_NAME = data["APP_NAME"]
        HTTP_PROXY = data["HTTP_PROXY"]
        dbGaP = data["dbGaP"]

        GUN_MAIL = data.get("GUN_MAIL")
