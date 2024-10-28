import pytest


from amanuensis.errors import InternalError
from amanuensis.resources.project import get_overall_project_state
from amanuensis import app
#from amanuensis.errors import InternalError 

#test errors

def test_incorrect_data():
    with pytest.raises(InternalError) as e:
        state = {"NOT_A_VALID_STATE"}
        result = get_overall_project_state(state)

    assert str(e.value) == "[500] - Unable to load or find the consortium status"

def test_correct_and_incorrect_data():
    with app.app_context():
        with pytest.raises(InternalError) as e:
            state = {"SUBMITTED", "NOT_A_VALID_STATE"}
            result = get_overall_project_state(state)

        assert str(e.value) == "[500] - Unable to load or find the consortium status"

def test_no_data():
    with app.app_context():
        result = get_overall_project_state({})
        # assert result == {"status": None}
        project_status = result['status'] if result['status'] else "ERROR"
        assert project_status == "ERROR"


#test correctness

def test_published():
    with app.app_context():
        assert get_overall_project_state({"PUBLISHED"}) == {"status": "PUBLISHED"}

def test_data_downloaded():
    with app.app_context():
        assert get_overall_project_state({"PUBLISHED", "DATA_DOWNLOADED"}) == {"status": "PUBLISHED"}

