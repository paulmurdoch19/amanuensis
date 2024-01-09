from amanuensis.models import State
import pytest
from amanuensis.resources.userdatamodel import create_state, get_state_by_code, get_state_by_id, get_all_states


@pytest.fixture(scope="module", autouse=True)
def states(session):

    state_1 = State(name="STATE1", code="STATE1")
    state_2 = State(name="STATE2", code="STATE2")
    session.add_all(
        [
            state_1,
            state_2
        ]
    )

    session.commit()

    yield state_1, state_2

    session.query(State).filter(State.code == "STATE1").delete()
    session.query(State).filter(State.code == "STATE2").delete()

    session.commit()

def test_create_state(session):
    data = create_state(session, name="TEST", code="TEST")
    assert data.code == session.query(State.code).filter(State.code == "TEST").first()[0]
    session.query(State).filter(State.code == "TEST").delete()


def test_get_state_by_code(session, states):
    data = get_state_by_code(session, "STATE1")
    assert states[0].id == data.id

def test_get_state_by_id(session, states):
    data = get_state_by_id(session, states[0].id)
    assert data.id == states[0].id

#note this will fail if the states are changed in the future, its total amount of states in DB +2 for the tests above
def test_get_all_states(session):
    assert len(get_all_states(session)) == 16