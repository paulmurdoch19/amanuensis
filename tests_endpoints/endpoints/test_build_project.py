import pytest
from mock import patch
from cdislogging import get_logger
from amanuensis.models import *
import json as j

logger = get_logger(logger_name=__name__)


# fence_users = {
#     "users": [
#         {
#             "first_name": "paul",
#             "id": 24,
#             "institution": "uchicago",
#             "last_auth": "Fri, 19 Jan 2024 20:33:37 GMT",
#             "last_name": "murdoch",
#             "name": "pmurdoch@uchicago.edu",
#             "role": "admin"
#         },
#         {
#             "first_name": "Paul",
#             "id": 26,
#             "institution": "university of chicago",
#             "last_auth": "Fri, 19 Jan 2024 20:33:19 GMT",
#             "last_name": "Murdoch",
#             "name": "paulmurdoch19@gmail.com",
#             "role": "user"
#         }
#     ]
# }
#helper functions
def patch_current_user_id(value):
    """
    Helper function to patch 'current_user.id' with a dynamic value.
    """
    return patch('amanuensis.blueprints.filterset.current_user', id=value)

def patch_get_consortium_list(consortium_list):
    return patch('amanuensis.resources.project.get_consortium_list', return_value=consortium_list)

def patch_current_user_project(id, username):
    return patch('amanuensis.blueprints.project.current_user', id=id, username=username)

def patch_fence_users(file, fence_users):
    return patch(f'{file}.fence_get_users', return_value=fence_users)

def create_filter_set(client, current_user_id, json, filter_source_internal_id=1):
    with patch_current_user_id(value=current_user_id):
        response = client.post(f'/filter-sets?explorerId={filter_source_internal_id}', json=json)
        return response

def get_filter_sets(client, current_user_id, filter_source_internal_id=1):
    with patch_current_user_id(value=current_user_id):
        response = client.get(f'/filter-sets?explorerId={filter_source_internal_id}')
        return response

def get_filter_set_by_id(client, current_user_id, filter_set_id, filter_source_internal_id=1):
    with patch_current_user_id(value=current_user_id):
        response = client.get(f'/filter-sets/{filter_set_id}?explorerId={filter_source_internal_id}')
        return response

def update_search(client):
    pass

def get_all_states(client):
    return client.get('/admin/states')

def endpoint_user_1(session):
    endpoint_user_1 = session.query(AssociatedUser).filter(AssociatedUser.email == "endpoint_user_1@test.com").first()

    if not endpoint_user_1:
        endpoint_user_1 = AssociatedUser(
                            user_id=100,
                            user_source='fence',
                            email='endpoint_user_1@test.com',
                            active=True
                        )
        session.add(endpoint_user_1)
        session.commit()
    return endpoint_user_1

def admin_user(session):
    admin = session.query(AssociatedUser).filter(AssociatedUser.email == "admin@test.com").first()

    if not admin:
        admin = AssociatedUser(
                            user_id=101,
                            user_source='fence',
                            email='admin@test.com',
                            active=True
                        )
        session.add(admin)
        session.commit()
    return admin

def create_admin_project(client, current_user_id, consortium_list, json):
    with patch_get_consortium_list(consortium_list):
        response = client.post('/admin/projects', json=json)
        return response

def get_projetcs(client, current_user_id, current_user_email, fence_users, special_user=None):
    with patch_current_user_project(current_user_id, current_user_email), patch_fence_users('amanuensis.blueprints.project', fence_users):
        if special_user:
            return client.get(f"/projects?special_user={special_user}")
        else:
            return client.get("/projects", headers={"Authorization": "bearer 1.2.3"})

#admin
def test_add_consortium(session, client):
    json = {"name": "ENDPOINT_TEST", "code": "ENDPOINT_TEST"}
    response = client.post("/admin/consortiums", json=json)
    assert response.status_code == 200
    assert session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "ENDPOINT_TEST").first().id == response.json["id"]
    session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "ENDPOINT_TEST").delete()
    session.commit()

def test_1_get_all_states(client):
    response = get_all_states(client)
    required_states = {"IN_REVIEW", "DATA_DOWNLOADED", "APPROVED"}
    for state in response.json:
        if state["code"] in required_states:
            required_states.remove(state["code"])
    if required_states:
        logger.error(f"state(s) {required_states} not present in DB")
        assert False
    else:
        assert True

def test_add_state(session, client):
    json = {"name": "ENDPOINT_TEST", "code": "ENDPOINT_TEST"}
    response = client.post("/admin/states", json=json)
    assert response.status_code == 200
    assert session.query(State).filter(State.code == "ENDPOINT_TEST").first().id == response.json["id"]
    session.query(State).filter(State.code == "ENDPOINT_TEST").delete()
    session.commit()

def test_2_filter_set(session, client):
    #all should test good, bad and no data
    #add 2 filters for user and 1 for admin
    #use get / route with user
    #use get /id route with user filter 1
    #use get admin/filter-sets/user for admin
    #use put /id route with user filter 2
    #user delete on user filter 2

    #create test_filter_set with user_1
    json = {"name":"test_filter_set",
            "description":"",
            "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","selectedValues":["INRG"],"isExclusion":False},
                                                                        "sex":{"__type":"OPTION","selectedValues":["Male"],"isExclusion": False}}},
            "gqlFilter":{"AND":[{"IN":{"consortium":["INRG"]}},{"IN":{"sex":["Male"]}}]}}
    response = create_filter_set(client, 100, json)
    assert response.status_code == 200

    # #create test_filter_set_2 with user_2
    # json = {"name":"test_filter_set_2",
    #         "description":"",
    #         "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","selectedValues":["INSTRuCT"],"isExclusion":False},"sex":{"__type":"OPTION","selectedValues":["Male"],"isExclusion":False}}},
    #         "gqlFilter":{"AND":[{"IN":{"consortium":["INSTRuCT"]}},{"IN":{"sex":["Male"]}}]}
    #         }
    # response = create_filter_set(client, 100, json)
    # assert response.status_code == 200

    response = get_filter_sets(client, 100)
    #prepare data 
    payload = {}
    payload["user_id"] = 100
    payload["name"] = "test project"
    payload["description"] = "this is a test project"
    payload["institution"] = "university of chicago"

    filter_set_ids = []
    for filter in response.json['filter_sets']:
        filter_set_ids.append(filter['id'])
    
    payload["filter_set_ids"] = filter_set_ids
    payload["associated_users_emails"] = ['admin@test.com', 'endpoint_user_1@test.com']
    response = create_admin_project(client, 101, ['INRG'], payload)
    assert response.status_code == 200

    fence_users = {
        "users": [
            {
                "first_name": "admin_endpoint_user",
                "id": 100,
                "institution": "uchicago",
                "last_auth": "Fri, 19 Jan 2024 20:33:37 GMT",
                "last_name": "admin_endpoint_user_last",
                "name": "endpoint_user_1@test.com",
                "role": "admin"
            }
        ]
    }


    response = get_projetcs(client, 100, 'endpoint_user_1@test.com', fence_users)
    assert response.status_code == 200
    print(response.json)
    assert False
    #create test_filter_set_admin with admin

