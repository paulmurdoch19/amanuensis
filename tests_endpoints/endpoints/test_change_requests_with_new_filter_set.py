import pytest
from mock import patch
from cdislogging import get_logger
from amanuensis.models import *
from amanuensis.schema import *
from datetime import datetime
import time
from sqlalchemy.orm import aliased
from amanuensis.blueprints.filterset import UserError
from amanuensis.resources.userdatamodel import get_project_by_id
from amanuensis.resources.userdatamodel.userdatamodel_state import get_latest_request_state_by_id
from sqlalchemy import func, desc
logger = get_logger(logger_name=__name__)


def test_change_requests_with_new_filter_set(app_instance, session, client, fence_get_users_mock, fence_users):
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

            # INSTRUCT_id = session.query(Request.id).filter(Request.project_id == project_id and Request.consortium_data_contributor.code == 'INSTRUCT').first()

            # INSTRUCT_curr_state = session.query(RequestState).filter(RequestState.request_id == INSTRUCT_id).order_by(RequestState.create_date.desc()).first()

            # IN_REVIEW = session.query(State).filter(State.id == )
            
            INRG = (
                    session
                    .query(Request)
                    .filter(Request.project_id == project_id)
                    .join(ConsortiumDataContributor, Request.consortium_data_contributor)
                    .filter(ConsortiumDataContributor.code == "INRG").first()
            )
            INSTRUCT = (
                    session
                    .query(Request)
                    .filter(Request.project_id == project_id)
                    .join(ConsortiumDataContributor, Request.consortium_data_contributor)
                    .filter(ConsortiumDataContributor.code == "INSTRUCT").first()
            )

            INTERACT = (
                    session
                    .query(Request)
                    .filter(Request.project_id == project_id)
                    .join(ConsortiumDataContributor, Request.consortium_data_contributor)
                    .filter(ConsortiumDataContributor.code == "INTERACT").first()
            )


            assert get_latest_request_state_by_id(session, INRG.id).state.code == "IN_REVIEW"
            assert get_latest_request_state_by_id(session, INSTRUCT.id).state.code == "IN_REVIEW"
            assert get_latest_request_state_by_id(session, INTERACT.id).state.code == "IN_REVIEW"


            update_project_state_approved_state_json = {"project_id": project_id, "state_id": approved_state["id"]}
            update_project_state_approved_state_response = client.post("/admin/projects/state", json=update_project_state_approved_state_json, headers={"Authorization": 'bearer 200'})
            update_project_state_approved_state_response.status_code == 200

        with \
        patch('amanuensis.blueprints.admin.current_user', id=200, username="admin@uchicago.edu"), \
        patch('amanuensis.resources.project.get_consortium_list', return_value=["INSTRuCT"]):
            admin_copy_search_to_project_json = {
                "filtersetId": id_2_requests,
                "projectId": project_id
            }
            admin_copy_search_to_project_response = client.post("admin/copy-search-to-project", json=admin_copy_search_to_project_json, headers={"Authorization": 'bearer 200'})
            assert admin_copy_search_to_project_response.status_code == 200

            request_schema = RequestSchema()
            def get_latest_state(req):
                session.refresh(req)
                request = request_schema.dump(req)
                print(request['id'])
                current_state = None
                for request_state in request['request_has_state']:
                    code = request_state['state']['code']
                    time = datetime.fromisoformat(request_state['create_date'])
                    if not current_state:
                        current_state = (code, time)
                    elif time > current_state[1]:
                        current_state = (code, time)

                return current_state[0]
            

            assert get_latest_state(INSTRUCT) == "IN_REVIEW"
            assert get_latest_state(INTERACT) == "WITHDRAWAL"
            assert get_latest_state(INRG) == "WITHDRAWAL"
        