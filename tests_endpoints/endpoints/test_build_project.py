import pytest
from mock import patch
from cdislogging import get_logger
from amanuensis.models import *
from amanuensis.schema import *
from datetime import datetime
from amanuensis.blueprints.filterset import UserError

logger = get_logger(logger_name=__name__)


def fence_get_users_mock(config=None, usernames=None, ids=None):
    '''
    amanuensis sends a request to fence for a list of user ids 
    matching the supplied list of user email addresses
    '''
    if (ids and usernames):
        logger.error("fence_get_users: Wrong params, only one among `ids` and `usernames` should be set.")
        return {}


    if usernames:
        queryBody = {
            'usernames': usernames
        }
    elif ids:
        queryBody = {
            'ids': ids
        }
    else:
        logger.error("fence_get_users: Wrong params, at least one among `ids` and `usernames` should be set.")
        return {}
    fence_users = [
        {
            "first_name": "endpoint_user_1",
            "id": 101,
            "institution": "test university",
            "last_auth": "Fri, 19 Jan 2024 20:33:37 GMT",
            "last_name": "endpoint_user_last_1",
            "name": "endpoint_user_1@test.com",
            "role": "user"
        },
        {
            "first_name": "endpoint_user_2",
            "id": 102,
            "institution": "test university",
            "last_auth": "Fri, 19 Jan 2024 20:33:37 GMT",
            "last_name": "endpoint_user_last",
            "name": "endpoint_user_2@test.com",
            "role": "user"
        },
        {
            "first_name": "endpoint_user_3",
            "id": 103,
            "institution": "test university",
            "last_auth": "Fri, 19 Jan 2024 20:33:37 GMT",
            "last_name": "endpoint_user_last_3",
            "name": "endpoint_user_3@test.com",
            "role": "user"
        },
        {
            "first_name": "admin_first",
            "id": 200,
            "institution": "uchicago",
            "last_auth": "Fri, 20 Jan 2024 20:33:37 GMT",
            "last_name": "admin_last",
            "name": "admin@uchicago.edu",
            "role": "admin"
        }
    ]
    return_users = {"users": []}
    for user in fence_users:
        if 'ids' in queryBody:
            if user['id'] in queryBody['ids']:
                return_users['users'].append(user)
        else:
            if user['name'] in queryBody['usernames']:
                return_users['users'].append(user)
    return return_users



def test_add_consortium(session, client):
    json = {"name": "ENDPOINT_TEST", "code": "ENDPOINT_TEST"}
    response = client.post("/admin/consortiums", json=json)
    assert response.status_code == 200
    assert session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "ENDPOINT_TEST").first().id == response.json["id"]
    session.query(ConsortiumDataContributor).filter(ConsortiumDataContributor.code == "ENDPOINT_TEST").delete()
    session.commit()

def test_add_state(session, client):
    json = {"name": "ENDPOINT_TEST", "code": "ENDPOINT_TEST"}
    response = client.post("/admin/states", json=json)
    assert response.status_code == 200
    assert session.query(State).filter(State.code == "ENDPOINT_TEST").first().id == response.json["id"]
    session.query(State).filter(State.code == "ENDPOINT_TEST").delete()
    session.commit()


def test_2_create_project_with_one_request(session, client):
    """
    this test will test the process of 3 pcdc users creating a project request
    add admin and user_2 to amanuensis DB
    """
    admin = AssociatedUser(user_id=200, email='admin@uchicago.edu')
    user_2 = AssociatedUser(user_id=102, email='endpoint_user_2@test.com')
    session.add_all([admin, user_2])
    session.commit()

    
    with patch('amanuensis.blueprints.filterset.current_user', id=101, username="endpoint_user_1@test.com"):
        
        """
        user_1 creates a filterset
        """

        filter_set_create_json = {
            "name":"test_filter_set",
            "description":"",
            "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","selectedValues":["INSTRuCT"],"isExclusion":False},"sex":{"__type":"OPTION","selectedValues":["Male"],"isExclusion":False}}},
            "gqlFilter":{"AND":[{"IN":{"consortium":["INSTRuCT"]}},{"IN":{"sex":["Male"]}}]}
        }
        filter_set_create_response = client.post(f'/filter-sets?explorerId=1', json=filter_set_create_json)
        assert filter_set_create_response.status_code == 200

        """
        user_1 sends a request to reterive the id of that filterset
        """

        filter_set_get_response = client.get('/filter-sets?explorerId=1')
        assert filter_set_get_response.status_code == 200


        id = filter_set_get_response.json["filter_sets"][0]["id"]

        """
        user_1 creates a snapshot of the filterset to share with user_2
        """

        filter_set_snapshot_json = {
            "filterSetId": id
        }
        snapshot_response = client.post("/filter-sets/snapshot", json=filter_set_snapshot_json)
        assert snapshot_response.status_code == 200

        """
        trigger Usererror test
        """
        response = client.post("/filter-sets/snapshot", json={})
        assert response.status_code == 400

    """
    user_2 access filter_set
    """

    with patch('amanuensis.blueprints.filterset.current_user', id=102, username="endpoint_user_2@test.com"):
        #other user gets snapshot
        
        get_snapshot_response = client.get(f"/filter-sets/snapshot/{snapshot_response.json}")
        assert get_snapshot_response.status_code == 200
        #assert get_snapshot_response.json["name"] == id
    
    
    """
    user_2 wants user_1 to make a change to the filter_set
    """

    with patch('amanuensis.blueprints.filterset.current_user', id=101, username="endpoint_user_1@test.com"):
        filter_set_change_json = {
            "description":"",
            "ids":None,
            "name":"test_filter_set",
            "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","isExclusion":False,"selectedValues":["INSTRuCT"]},"sex":{"__type":"OPTION","isExclusion":False,"selectedValues":["Male","Female"]}}},
            "gqlFilter":{"AND":[{"IN":{"consortium":["INSTRuCT"]}},{"IN":{"sex":["Male","Female"]}}]}
        }
        filter_set_create_response = client.put(f'/filter-sets/{id}?explorerId=1', json=filter_set_change_json)
        assert filter_set_create_response.status_code == 200


    with \
    patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"), \
    patch('amanuensis.resources.project.get_consortium_list', return_value=["INSTRUCT"]):


        """
        admin fetches the filter sets from user_1
        """

        admin_get_filter_sets_json = {"user_id": 101}
        admin_get_filter_sets = client.get("/admin/filter-sets/user", json=admin_get_filter_sets_json)
        assert admin_get_filter_sets.status_code == 200
        assert admin_get_filter_sets.json["filter_sets"][0]['id'] == id
        
        """
        ERROR TEST
        """
        error_response = client.get("/admin/filter-sets/user", json={})
        assert error_response.status_code == 400

        """
        admin creates a new project
        """

        create_project_json = {
            "user_id": 101,
            "name": "Test Project",
            "description": "This is an endpoint test project",
            "institution": "test university",
            "filter_set_ids": [admin_get_filter_sets.json["filter_sets"][0]['id']],
            "associated_users_emails": ["endpoint_user_1@test.com", "admin@uchicago.edu"]

        }
        create_project_response = client.post('/admin/projects', json=create_project_json)
        assert create_project_response.status_code == 200
        project_id = create_project_response.json['id']

        """
        TEST ERROR
        """
        error_response  = client.post('/admin/projects', json={})
        assert error_response.status_code == 400

        with patch('amanuensis.resources.project.get_consortium_list', return_value=["bad"]):
            error_response = client.post('/admin/projects', json=create_project_json)
            assert error_response.status_code == 404
        

        
        """
        add user_2 to the project with data access
        """
        with patch("amanuensis.resources.admin.admin_associated_user.fence.fence_get_users", side_effect=fence_get_users_mock):
            add_user_2_response = client.post("/admin/associated_user", json={"users": [{"project_id": project_id, "email": 'endpoint_user_2@test.com'}], "role": "DATA_ACCESS"})
            add_user_2_response.status_code == 200
        
        """
        add user_3 to the project with metadata access
        """
        
        with patch("amanuensis.resources.admin.admin_associated_user.fence.fence_get_users", side_effect=fence_get_users_mock):
            add_user_3_response = client.post("/admin/associated_user", json={"users": [{"project_id": project_id, "email": 'endpoint_user_3@test.com'}]})
            add_user_3_response.status_code == 200
        

        """
        send a request to reterive all the possible roles
        """
        roles_response = client.get("/admin/all_associated_user_roles")
        assert roles_response.status_code == 200
        data_access = roles_response.json["DATA_ACCESS"]

        """
        change user_1's role to Data Access
        """
        user_1_data_acess_json = {
            "user_id": 101,
            "email": "endpoint_user_1@test.com",
            "project_id": project_id,
            "role": data_access
        }
        user_1_data_acess_response = client.put("/admin/associated_user_role", json=user_1_data_acess_json)
        assert user_1_data_acess_response.status_code == 200
        
        user_3_data_acess_json = {
            "user_id": 103,
            "email": "endpoint_user_3@test.com",
            "project_id": project_id,
            "role": data_access
        }
        user_3_data_acess_response = client.put("/admin/associated_user_role", json=user_3_data_acess_json)
        assert user_3_data_acess_response.status_code == 200


        """
        remove user_3 from the project
        """
        user_3_delete_json = {
            "user_id": 103,
            "email": "endpoint_user_3@test.com",
            "project_id": project_id,
        }
        user_3_delete_response = client.delete("/admin/associated_user_role", json=user_3_delete_json)
        assert user_3_delete_response.status_code == 200



        """
        send a request to retreve all availble options for project states
        """


        revision_state = None
        approved_state = None
        data_available = None
        get_states_response = client.get("/admin/states")
        for state in get_states_response.json:
            if state["code"] == "REVISION":
                revision_state = state
            elif state["code"] == "APPROVED":
                approved_state = state
            elif state["code"] == "DATA_AVAILABLE":
                data_available = state 




        """
        the EC committe requires the users to change their filter set, move state to revision
        """

        update_project_state_revison_json = {"project_id": project_id, "state_id": revision_state["id"]}
        update_project_state_revison_response = client.post("/admin/projects/state", json=update_project_state_revison_json)
        update_project_state_revison_response.status_code == 200



        """
        admin creates a filter_set with the corrections
        """
        admin_create_filter_set_json = {
            "user_id": 200,
            "name":"test_filter_set_correction",
            "description":"",
            "filters":{"AND":[{"IN":{"consortium":["INSTRuCT"]}}]}
        }
        admin_create_filter_set_response = client.post("/admin/filter-sets", json=admin_create_filter_set_json)
        assert admin_create_filter_set_response.status_code == 200

        admin_filterset_id = admin_create_filter_set_response.json["id"]

        """
        TEST ERROR no user_id
        """
        
        error_response  = client.post("/admin/filter-sets", json={})
        assert error_response.status_code == 400

        """
        admin copies new search to user_1
        """

        admin_copy_search_to_user_json = {
            "filtersetId": admin_filterset_id,
            "userId": 101
        }
        admin_copy_search_to_user_response = client.post("admin/copy-search-to-user", json=admin_copy_search_to_user_json)
        admin_copy_search_to_user_response.status_code == 200


        
        """
        admin copies new search to the project
        """

        admin_copy_search_to_project_json = {
            "filtersetId": admin_filterset_id,
            "projectId": project_id
        }
        admin_copy_search_to_project_response = client.post("admin/copy-search-to-project", json=admin_copy_search_to_project_json)
        assert admin_copy_search_to_project_response.status_code == 200



        """
        move project state to approved
        """

        update_project_state_approved_json = {"project_id": project_id, "state_id": approved_state["id"]}
        update_project_state_approved_response = client.post("/admin/projects/state", json=update_project_state_approved_json)
        assert update_project_state_approved_response.status_code == 200

        """
        add approved_url to project
        """
        update_project_json = {
            "project_id": project_id,
            "approved_url": "http://approved.com"
        }
        update_project_response = client.put("/admin/projects", json=update_project_json)
        assert update_project_response.status_code == 200

        """
        Error test
        """
        #assert client.put("/admin/projects", json={}).status_code == 400

        """
        patch project date
        """
        #BUG test current disabled do to bug
        # current_time = datetime.now()
        # patch_project_date_json = {
        #     "project_id": project_id,
        #     "year": current_time.year,
        #     "month": current_time.month,
        #     "day": current_time.day
        # }
        # patch_project_date_response = client.patch("/admin/projects/date", json=patch_project_date_json)
        # assert patch_project_date_response.status_code == 200


        """
        move state to data availble
        """

        update_project_state_data_available_json = {"project_id": project_id, "state_id": data_available["id"]}
        update_project_state_data_available_response = client.post("/admin/projects/state", json=update_project_state_data_available_json)
        update_project_state_data_available_response.status_code == 200

        """
        error test
        """
        #assert client.post("/admin/projects/state", json={}).status_code == 400

    with \
    patch('amanuensis.blueprints.download_urls.current_user', id=102, username="endpoint_user_2@test.com"), \
    patch('amanuensis.blueprints.download_urls.get_s3_key_and_bucket', return_value={"bucket": "test_bucket", "key": "test_key"}):
        """
        get download url
        """
        get_download_url_response_2 = client.get(f"/download-urls/{project_id}")
        assert get_download_url_response_2.status_code == 200
    
    with \
    patch('amanuensis.blueprints.download_urls.current_user', id=103, username="endpoint_user_3@test.com"):
        """
        test user_3 cannot get downloaded url (not active)
        """
        get_download_url_response_3 = client.get(f"/download-urls/{project_id}")
        assert get_download_url_response_3.status_code == 403
    


    # with \
    # patch('amanuensis.blueprints.download_urls.current_user', id=101, username="endpoint_user_1@test.com"):
    #     """
    #     test user_1 cannot get donwloaded url (no user_id)
    #     """
    #     get_download_url_response_1 = client.get(f"/download-urls/{project_id}")
    #     assert get_download_url_response_1.status_code == 403

    with \
    patch('amanuensis.blueprints.download_urls.current_user', id=200, username="admin@uchicago.edu"):
        """
        test user_1 cannot get downloaded url (metadata access)
        """
        get_download_url_response_admin = client.get(f"/download-urls/{project_id}")
        assert get_download_url_response_admin.status_code == 403


        """
        run all three get project requests
        """
    with \
    patch('amanuensis.blueprints.project.current_user', id=101, username="endpoint_user_1@test.com"), \
    patch('amanuensis.blueprints.project.has_arborist_access', return_value=False), \
    patch("amanuensis.blueprints.project.fence_get_users", side_effect=fence_get_users_mock):
        get_project_user_1_response = client.get("/projects", headers={"Authorization": 'bearer 1.2.3'})
        assert get_project_user_1_response.status_code == 200
        user_1_first_login = session.query(AssociatedUser).filter(AssociatedUser.email == "endpoint_user_1@test.com").first()
        assert user_1_first_login.user_id == 101
    
    with \
    patch('amanuensis.blueprints.project.current_user', id=100, username="FAKEUSER"), \
    patch('amanuensis.blueprints.project.has_arborist_access', return_value=False):
        """
        TEST ERROR
        """
        assert client.get("/projects", headers={"Authorization": 'bearer 1.2.3'}).status_code == 404


    with patch('amanuensis.blueprints.filterset.current_user', id=101, username="endpoint_user_1@test.com"):
        """
        user_1 gets the filterset with the filterset id
        """
        get_filter_set_id_response = client.get(f"filter-sets/{id}?explorerId=1")
        assert get_filter_set_id_response.status_code == 200


        """
        user_1 deletes the filterset as the project is now complete
        """
        delete_filter_set = client.delete(f"filter-sets/{id}?explorerId=1")
        assert delete_filter_set.status_code == 200 
    


        