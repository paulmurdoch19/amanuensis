
import requests
import json
import os

from amanuensis.auth import sign
from amanuensis.auth.auth import get_jwt_from_header
from amanuensis.auth.errors import NoPrivateKeyError
from cdislogging import get_logger


logger = get_logger(__name__)


def fence_get_users(usernames, config):
    '''
    amanuensis sends a request to fence for a list of user ids 
    matching the supplied list of user email addresses
    '''
    queryBody = {
        'usernames': usernames
    }

    # logger.info(f"queryBody usernames: {usernames}")

    try:
        url = 'http://fence-service/admin/users/selected'  
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(queryBody)
        jwt = get_jwt_from_header()
        priv_key = config["RSA_PRIVATE_KEY"]
        headers['Authorization'] = 'bearer ' + jwt
        headers['Signature'] = b'signature ' + sign(body, priv_key)
        headers['Gen3-Service'] = str(os.environ.get('SERVICE_NAME', '')).encode('utf-8')

        # logger.info(f"headers: {str(headers)}")
        # logger.info(f"data: {str(body)}")
        # logger.info(f"url: {str(url)}")
        logger.info(f"fence_get_users url: {url}")
 
        r = requests.post(
            url, data=body, headers=headers
        )
        if r.status_code == 200:
          return r.json()

    except NoPrivateKeyError as e:
        print(e.message)
    except requests.HTTPError as e:
        print(e.message)

    return[]

