import pytest
from mock import patch
from cdislogging import get_logger
from amanuensis.models import *
from amanuensis.schema import *
from datetime import datetime
import time
from amanuensis.blueprints.filterset import UserError

logger = get_logger(logger_name=__name__)


def test_change_requests_with_new_filter_set(session, client, fence_get_users_mock, fence_users):
    #start with two consortiums
    #move to approved
    #change to 3 which should move all three to in review
    #move to approved
    #change back to 2 removing INTERACT
    #INTERACT should go to withdrawl
    #should the other two go back to in_review or stay what they are
    with \
    patch("amanuensis.resources.admin.admin_associated_user.fence.fence_get_users", side_effect=fence_get_users_mock), \
    patch("amanuensis.blueprints.project.fence_get_users", side_effect=fence_get_users_mock), \
    patch('amanuensis.blueprints.download_urls.get_s3_key_and_bucket', return_value={"bucket": "test_bucket", "key": "test_key"}):
        #create a filter-set with  consortiums
        with \
        patch('amanuensis.blueprints.filterset.current_user', id=102, username="endpoint_user_2@test.com"):
            filter_set_create_json = {
                "name":f"{__name__}_2_requests",
                "description":"",
                "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","selectedValues":["INSTRuCT"],"isExclusion":False},"sex":{"__type":"OPTION","selectedValues":["Male"],"isExclusion":False}}},
                "gqlFilter":{"AND":[{"IN":{"consortium":["INSTRuCT"]}},{"IN":{"sex":["Male"]}}]}
            }
            filter_set_create_response = client.post(f'/filter-sets?explorerId=1', json=filter_set_create_json, headers={"Authorization": 'bearer 102'})
            assert filter_set_create_response.status_code == 200

            id_2_requests = filter_set_create_response.json["id"]


        with \
        patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"), \
        patch('amanuensis.resources.project.get_consortium_list', return_value=["INSTRuCT"]):
            create_project_json = {
                "user_id": 102,
                "name": f"{__name__}",
                "description": f"this is the project for {__name__}",
                "institution": "test university",
                "filter_set_ids": [id_2_requests],
                "associated_users_emails": []

            }
            create_project_response = client.post('/admin/projects', json=create_project_json, headers={"Authorization": 'bearer 200'})
            assert create_project_response.status_code == 200
            project_id = create_project_response.json['id']

            approved_state = None
            get_states_response = client.get("/admin/states", headers={"Authorization": 'bearer 200'})
            for state in get_states_response.json:
                if state["code"] == "APPROVED":
                    approved_state = state


            update_project_state_approved_state_json = {"project_id": project_id, "state_id": approved_state["id"]}
            update_project_state_approved_state_response = client.post("/admin/projects/state", json=update_project_state_approved_state_json, headers={"Authorization": 'bearer 200'})
            update_project_state_approved_state_response.status_code == 200

        with \
        patch('amanuensis.blueprints.filterset.current_user', id=102, username="endpoint_user_2@test.com"):
            filter_set_create_json = {
                "name":f"{__name__}_3_requests",
                "description":"",
                "filters":{"__combineMode":"AND","__type":"STANDARD","value":{"consortium":{"__type":"OPTION","selectedValues":["INSTRuCT", "INRG", "INTERACT"],"isExclusion":False},"sex":{"__type":"OPTION","selectedValues":["Male"],"isExclusion":False}}},
                "gqlFilter":{"AND":[{"IN":{"consortium":["INSTRuCT", "INRG", "INTERACT"]}},{"IN":{"sex":["Male"]}}]}
            }
            filter_set_create_response = client.post(f'/filter-sets?explorerId=1', json=filter_set_create_json, headers={"Authorization": 'bearer 102'})
            assert filter_set_create_response.status_code == 200

            id_3_requests = filter_set_create_response.json["id"]
        

        with \
        patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"), \
        patch('amanuensis.resources.project.get_consortium_list', return_value=["INSTRuCT", "INRG", "INTERACT"]):
            admin_copy_search_to_project_json = {
                "filtersetId": id_3_requests,
                "projectId": project_id
            }
            admin_copy_search_to_project_response = client.post("admin/copy-search-to-project", json=admin_copy_search_to_project_json, headers={"Authorization": 'bearer 200'})
            assert admin_copy_search_to_project_response.status_code == 200