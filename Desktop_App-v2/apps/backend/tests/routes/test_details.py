import pytest
from flask.testing import FlaskClient   #for type hint
from ..helpers import generate_node, generate_question, build_test_ll

class TestAddDetailRoutes:
    def test_add_detail_cannot_add_empty_detail(self, test_client:FlaskClient):
        new_detail = ""
        response_invalid_1 = test_client.post("/add_detail", data=new_detail)
        assert response_invalid_1.status_code == 404

    def test_add_detail_cannot_add_existing_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2"]
        new_detail = "1"

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)

        response_invalid_2 = test_client.post("/add_detail", data=new_detail)
        assert response_invalid_2.status_code == 409

    def test_add_detail_can_add_new_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2"]
        new_detail = "3"
        expected = ["1", "2", "3"]

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)

        response_valid = test_client.post("/add_detail", data=new_detail)
        assert response_valid.status_code == 200
        result = response_valid.get_json()
        assert result["all_details"] == expected

class DeleteDetailRoutes:
    def test_delete_detail_cannot_remove_empty_detail(self, test_client:FlaskClient):
        new_detail = ""
        response_invalid_1 = test_client.delete("/delete_detail", data=new_detail)
        assert response_invalid_1.status_code == 404

    def test_delete_detail_cannot_remove_nonexistent_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2"]
        new_detail = "3"

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)

        response_invalid_2 = test_client.delete("/delete_detail", data=new_detail)
        assert response_invalid_2.status_code == 409

    def test_delete_detail_can_remove_existing_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2", "3"]
        new_detail = "2"
        expected = ["1", "3"]

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)

        response_valid = test_client.delete("/delete_detail", data=new_detail)
        assert response_valid.status_code == 200
        result = response_valid.get_json()
        assert result["all_details"] == expected

def test_clear_details_clears_all_details(test_client:FlaskClient, test_session):
    sess_var = {"all_details": ["1", "2"]}
    test_session(test_client, sess_var)

    response = test_client.delete("/clear_details")
    assert response.status_code == 200
    assert response.text == "All, if any, details deleted. all_details is now []"

def test_get_base_details_can_get_base_q_details(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="1", q_type="singular"))
    node_2 = generate_node(generate_question(q_detail="2", q_type="base"))
    node_3 = generate_node(generate_question(q_detail="3", q_type="base"))
    node_4 = generate_node(generate_question(q_detail="4", q_type="singular"))
    build_test_ll(test_client, nodes=[node_1, node_2, node_3, node_4])

    response = test_client.get("/get_base_details")
    assert response.status_code == 200
    result = response.get_json()
    assert result["base_q_details"] == ["2", "3"]

@pytest.mark.parametrize("detail_exist", [True, False])
def test_check_detail_can_check_if_detail_in_all_details(test_client:FlaskClient, test_session, detail_exist):
    details = ["1", "2"]
    if detail_exist:
        detail = "1"
    else:
        detail = "3"

    sess_var = {"all_details": details}
    test_session(test_client, sess_var)
    
    response = test_client.get(f"/check_detail/{detail}")
    assert response.status_code == 200
    result = response.get_json()
    assert result == {"exists":str(detail_exist).lower(),"all_details":details}