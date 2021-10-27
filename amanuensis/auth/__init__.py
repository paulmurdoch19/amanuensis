from os import environ
import binascii
from cdislogging import get_logger
from amanuensis.auth.errors import NoPrivateKeyError
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256



logger = get_logger(__name__)


def loadkey():
    """
    Load private key
    """
    priv_key = None
    private_key_path = environ.get("PRIVATE_KEY_PATH", None)
    
    if private_key_path is None:
        logger.error("ERROR - PRIVATE KEY PATH NOT SET!")
    else:
        with open(private_key_path, "r") as f:
            priv_key = RSA.import_key(f.read())

    if priv_key is None:
        logger.error("ERROR - PRIVATE KEY NOT LOADED!")
    
    return priv_key


def sign(body, priv_key):
    """
    Create signature for payload
    key preloaded with RSA.import_key during app_init call to loadkey() 
    and passed int here
    """
    if priv_key is None:
        raise NoPrivateKeyError("ERROR - Can't sign the message, no private key has been found.")

    hash = SHA256.new(body.encode('utf-8'))
    signature = pkcs1_15.new(priv_key).sign(hash)
    hexed_signature = binascii.hexlify(signature)
    return hexed_signature