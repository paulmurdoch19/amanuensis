from collections import OrderedDict
import os

from authutils.oauth2.client import blueprint as oauth2_blueprint
# from authutils.oauth2.client import OAuthClient
import flask
from flask_cors import CORS
from flask_sqlalchemy_session import flask_scoped_session, current_session
from userportaldatamodel.driver import SQLAlchemyDriver
from userportaldatamodel.models import Search

from amanuensis.errors import UserError
from amanuensis.models import migrate
from amanuensis.resources.aws.boto_manager import BotoManager

from amanuensis.error_handler import get_error_response
from amanuensis.config import config
from amanuensis.settings import CONFIG_SEARCH_FOLDERS
import amanuensis.blueprints.misc
import amanuensis.blueprints.filterset
import amanuensis.blueprints.project
import amanuensis.blueprints.request
import amanuensis.blueprints.message
import amanuensis.blueprints.admin

from pcdcutils.signature import SignatureManager

from cdislogging import get_logger

from cdispyutils.config import get_value

from gen3authz.client.arborist.client import ArboristClient

# Can't read config yet. Just set to debug for now, else no handlers.
# Later, in app_config(), will actually set level based on config
logger = get_logger(__name__)

app = flask.Flask(__name__)
CORS(app=app, headers=["content-type", "accept"], expose_headers="*")


def warn_about_logger():
    raise Exception(
        "Flask 0.12 will remove and replace all of our log handlers if you call "
        "app.logger anywhere. Use get_logger from cdislogging instead."
    )


def app_init(
    app,
    settings="amanuensis.settings",
    root_dir=None,
    config_path=None,
    config_file_name=None,
):
    app.__dict__["logger"] = warn_about_logger

    app_config(
        app,
        settings=settings,
        root_dir=root_dir,
        config_path=config_path,
        file_name=config_file_name,
    )

    app_sessions(app)
    app_register_blueprints(app)


def app_sessions(app):
    app.url_map.strict_slashes = False
    app.db = SQLAlchemyDriver(config["DB"])
    # app.db = SQLAlchemyDriver('postgresql://amanuensis_user:amanuensis_pass@postgres:5432/amanuensis_db')
    logger.warning("DB connected")
    # TODO: we will make a more robust migration system external from the application
    #       initialization soon
    if config["ENABLE_DB_MIGRATION"]:
        logger.info("Running database migration...")
        migrate(app.db)
        logger.info("Done running database migration.")
    else:
        logger.info("NOT running database migration.")

    session = flask_scoped_session(app.db.Session, app)  # noqa


def app_register_blueprints(app):
    # app.register_blueprint(amanuensis.blueprints.oauth2.blueprint, url_prefix="/oauth2")

    # creds_blueprint = amanuensis.blueprints.storage_creds.make_creds_blueprint()
    # app.register_blueprint(creds_blueprint, url_prefix="/credentials")

    app.register_blueprint(amanuensis.blueprints.admin.blueprint, url_prefix="/admin")
    # app.register_blueprint(
    #     amanuensis.blueprints.well_known.blueprint, url_prefix="/.well-known"
    # )

    # link_blueprint = amanuensis.blueprints.link.make_link_blueprint()
    # app.register_blueprint(link_blueprint, url_prefix="/link")

    # google_blueprint = amanuensis.blueprints.google.make_google_blueprint()
    # app.register_blueprint(google_blueprint, url_prefix="/google")

    app.register_blueprint(amanuensis.blueprints.filterset.blueprint, url_prefix="/filter-sets")
    app.register_blueprint(amanuensis.blueprints.project.blueprint, url_prefix="/projects")
    app.register_blueprint(amanuensis.blueprints.request.blueprint, url_prefix="/requests")
    app.register_blueprint(amanuensis.blueprints.message.blueprint, url_prefix="/message")
    
    app.register_blueprint(oauth2_blueprint.blueprint, url_prefix="/oauth2")

    amanuensis.blueprints.misc.register_misc(app)

    @app.route("/")
    def root():
        """
        Register the root URL.
        """
        endpoints = {
            "oauth2 endpoint": "/oauth2",
            "user endpoint": "/user",
            "keypair endpoint": "/credentials",
        }
        return flask.jsonify(endpoints)

    

    @app.route("/jwt/keys")
    def public_keys():
        """
        Return the public keys which can be used to verify JWTs signed by amanuensis.

        The return value should look like this:
            {
                "keys": [
                    {
                        "key-01": " ... [public key here] ... "
                    }
                ]
            }
        """
        return flask.jsonify(
            {"keys": [(keypair.kid, keypair.public_key) for keypair in app.keypairs]}
        )



# def _check_s3_buckets(app):
#     """
#     Function to ensure that all s3_buckets have a valid credential.
#     Additionally, if there is no region it will produce a warning then try to fetch and cache the region.
#     """
#     buckets = config.get("S3_BUCKETS") or {}
#     aws_creds = config.get("AWS_CREDENTIALS") or {}

#     for bucket_name, bucket_details in buckets.items():
#         cred = bucket_details.get("cred")
#         region = bucket_details.get("region")
#         if not cred:
#             raise ValueError(
#                 "No cred for S3_BUCKET: {}. cred is required.".format(bucket_name)
#             )

#         # if this is a public bucket, amanuensis will not try to sign the URL
#         # so it won't need to know the region.
#         if cred == "*":
#             continue

#         if cred not in aws_creds:
#             raise ValueError(
#                 "Credential {} for S3_BUCKET {} is not defined in AWS_CREDENTIALS".format(
#                     cred, bucket_name
#                 )
#             )

#         # only require region when we're not specifying an
#         # s3-compatible endpoint URL (ex: no need for region when using cleversafe)
#         if not region and not bucket_details.get("endpoint_url"):
#             logger.warning(
#                 "WARNING: no region for S3_BUCKET: {}. Providing the region will reduce"
#                 " response time and avoid a call to GetBucketLocation which you make lack the AWS ACLs for.".format(
#                     bucket_name
#                 )
#             )
#             credential = S3IndexedFileLocation.get_credential_to_access_bucket(
#                 bucket_name,
#                 aws_creds,
#                 config.get("MAX_PRESIGNED_URL_TTL", 3600),
#                 app.boto,
#             )
#             if not getattr(app, "boto"):
#                 logger.warning(
#                     "WARNING: boto not setup for app, probably b/c "
#                     "nothing in AWS_CREDENTIALS. Cannot attempt to get bucket "
#                     "bucket regions."
#                 )
#                 return

#             region = app.boto.get_bucket_region(bucket_name, credential)
#             config["S3_BUCKETS"][bucket_name]["region"] = region


def app_config(
    app, settings="amanuensis.settings", root_dir=None, config_path=None, file_name=None
):
    """
    Set up the config for the Flask app.
    """
    if root_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    logger.info("Loading settings...")
    # not using app.config.from_object because we don't want all the extra flask cfg
    # vars inside our singleton when we pass these through in the next step
    settings_cfg = flask.Config(app.config.root_path)
    settings_cfg.from_object(settings)

    # dump the settings into the config singleton before loading a configuration file
    config.update(dict(settings_cfg))

    # load the configuration file, this overwrites anything from settings/local_settings
    config.load(
        config_path=config_path,
        search_folders=CONFIG_SEARCH_FOLDERS,
        file_name=file_name,
    )

    # load all config back into flask app config for now, we should PREFER getting config
    # directly from the amanuensis config singleton in the code though.
    app.config.update(**config._configs)

    _setup_hubspot_key(app)
    _setup_arborist_client(app)
    # _setup_data_endpoint_and_boto(app)

    # app.storage_manager = StorageManager(config["STORAGE_CREDENTIALS"], logger=logger)

    app.debug = config["DEBUG"]
    # Following will update logger level, propagate, and handlers
    get_logger(__name__, log_level="debug" if config["DEBUG"] == True else "info")

    # load private key for cross-service access
    key_path = config.get("PRIVATE_KEY_PATH", None)
    config["RSA_PRIVATE_KEY"] = SignatureManager(key_path=key_path).get_key()

    # _check_s3_buckets(app)


# def _setup_data_endpoint_and_boto(app):
#     if "AWS_CREDENTIALS" in config and len(config["AWS_CREDENTIALS"]) > 0:
#         value = list(config["AWS_CREDENTIALS"].values())[0]
#         app.boto = BotoManager(value, logger=logger)
#         app.register_blueprint(amanuensis.blueprints.data.blueprint, url_prefix="/data")



def _setup_arborist_client(app):
    if app.config.get("ARBORIST"):
        app.arborist = ArboristClient(arborist_base_url=config["ARBORIST"])

def _setup_hubspot_key(app):
    if app.config.get("HUBSPOT"):
        if "API_KEY" in config["HUBSPOT"]:
            app.hubspot_api_key = config["HUBSPOT"]["API_KEY"]
        # else:
            #TODO throw error

@app.errorhandler(Exception)
def handle_error(error):
    """
    Register an error handler for general exceptions.
    """
    return get_error_response(error)
