import flask
import requests

import re

from json import dumps
from fence.config import config



def request_hubspot(data={}, method="POST", path="/"):
    url = "https://api.hubapi.com/crm/v3/objects" + path
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    querystring = {"hapikey": flask.current_app.hubspot_api_key}
    return requests.request(method, url, data=dumps(data), headers=headers, params=querystring)


#TODO is this used at all???
def is_domain(name):
    # copied from https://validators.readthedocs.io/en/latest/_modules/validators/domain.html
    pattern = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return pattern.match(name)


def get_user(email, hubspot_id):
    data = {
        "filterGroups": [{
            "filters": [{
                "value": email,
                "propertyName": "email",
                "operator": "EQ"
            }]
        }],
        "properties": ["firstname", "lastname", "institution"]
    }
    print("GET HUB USER")
    r = request_hubspot(data=data, path="/contacts/search")
    # {"total": 0, "results": []}
    r = r.json()
    if len(r.get("results")) < 1:
    	return None

    user_properties = r.get("results")[0].get("properties")
    return {
        "firstname": user_properties.get("firstname"),
        "lastname": user_properties.get("lastname"),
        "institution": user_properties.get("institution")
    }
    # return flask.jsonify({"user": {
    #     "firstname": user_properties.get("firstname"),
    #     "lastname": user_properties.get("lastname"),
    #     "institution": user_properties.get("institution"),
    # }})

def is_user(email, hubspot_id):
    data = {
        "filterGroups": [{
            "filters": [{
                "value": email,
                "propertyName": "email",
                "operator": "EQ"
            }]
        }],
        "properties": [""]
    }
    r = request_hubspot(data=data, path="/contacts/search")
    registered = r.json().get("total", 0) > 0
    # return flask.jsonify({"registered": registered})
    return registered

def update_user_info(email, user_info):
	#TODO call hubspot API and return id
	hubspot_id = None
	if is_user(email, None):
		hubspot_id = update_user(email, user_info)
	else:
		create_user(email, user_info)
		hubspot_id = 1

	return hubspot_id


def create_user(email, user_info):
    data = {
        "properties": {
            "email": email,
            "firstname": user_info["firstName"],
            "institution": user_info["institution"],
            "lastname": user_info["lastName"],
        }
    }
    print("CREATE HUB USER")
    r = request_hubspot(data=data, path="/contacts")
    print(r)
    print(r.json())
    print(dumps(r))
    success = r.status_code == requests.codes.created
    #TODO thrpw error if not success
    return flask.jsonify({"success": success})


def update_user(email, user_info):
    data_get = {
        "filterGroups": [{
            "filters": [{
                "value": email,
                "propertyName": "email",
                "operator": "EQ"
            }]
        }],
        "properties": [""]
    }
    print("UPDATES HUB USER")
    r_get = request_hubspot(data=data_get, path="/contacts/search")
    print(dumps(r_get))
    user_id = r_get.json().get("results")[0].get("id")

    data_update = {
        "properties": {
            "firstname": user_info["firstName"],
            "institution": user_info["institution"],
            "lastname": user_info["lastName"],
        }
    }
    r_update = request_hubspot(
        data=data_update, method="PATCH", path=f"/contacts/{user_id}")
    success = r_update.status_code == requests.codes.ok
    #TODO thrpw error if not success
    return user_id














# def register_arborist_user(user, policies=None):
#     if not hasattr(flask.current_app, "arborist"):
#         raise Forbidden(
#             "this fence instance is not configured with arborist;"
#             " this endpoint is unavailable"
#         )

#     created_user = flask.current_app.arborist.create_user(dict(name=user.username))

#     if policies is None:
#         policies = ["login_no_access", "analysis"]

#     for policy_name in policies:
#         policy = flask.current_app.arborist.get_policy(policy_name)
#         if not policy:
#             raise NotFound(
#                 "Policy {} NOT FOUND".format(
#                     policy_name
#                 )
#             )

#         res = flask.current_app.arborist.grant_user_policy(user.username, policy_name)
#         if res is None:
#             raise ArboristError(
#                 "Policy {} has not been assigned.".format(
#                     policy["id"]
#                 )
#             )







