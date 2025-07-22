# import pytest
# from flask.testing import FlaskClient   #for type hint
# from pytest_mock import MockerFixture   #for type hints
# from app.models import Question, Node, ExportData
# from ..helpers import build_test_export_data, build_test_ll, generate_node, generate_question

# def test_set_export_method_cannot_set_invalid_export_data_method(test_client:FlaskClient):
#     invalid_method = "json"
#     build_test_export_data(test_client)

#     response = test_client.post("/set_export_method", data=invalid_method)
#     assert response.status_code == 409

# def test_set_export_method_can_set_valid_export_data_method(test_client:FlaskClient):
#     valid_method = "csv"
#     build_test_export_data(test_client)

#     response = test_client.post("/set_export_method", data=valid_method)
#     assert response.status_code == 200
#     assert response.text == f"Method: {valid_method} set"


# def test_get_export_method_can_get_export_method(test_client:FlaskClient):
#     export_arg = {"method": "json"}
#     build_test_export_data(test_client, export_arg)

#     response = test_client.get("/get_export_method")
#     assert response.status_code == 200
#     assert response.text == "json"

# def test_set_answers_to_export_can_set_all_answers_to_export_data(test_client:FlaskClient):
#     node_1:Node = generate_node(generate_question(q_detail="1"))
#     node_2:Node = generate_node(generate_question(q_detail="2"))
#     node_3:Node = generate_node(generate_question(q_detail="3"))
#     node_1.answer = "a1"
#     node_2.answer = "a2"
#     node_3.answer = "a3"
#     nodes = [node_1, node_2, node_3]
#     build_test_ll(test_client, nodes=nodes)

#     build_test_export_data(test_client)

#     response = test_client.post("/set_answers_to_export")
#     assert response.status_code == 200
#     expected = ["a1", "a2", "a3"]
#     assert response.text == f"Answers {expected} added"

# @pytest.mark.parametrize("is_valid", [True, False])
# def test_set_sheet_id_can_only_set_valid_sheet_id(test_client:FlaskClient, mocker:MockerFixture, is_valid):
#     if is_valid:
#         ret_value = True, "Sheet exists and is accessible"
#     else:
#         ret_value = False, "Access denied: The given ID does not match to any Google Sheets file"
    
#     # build test export_data manually
#     app = test_client.application  # The Flask app instance
#     with app.app_context():
#         app.export_data = ExportData()
#         #patch over the validation to avoid having to connect to Google API rn
#         mocker.patch.object(app.export_data, "_validate_sheet_id", return_value=ret_value)

#     response = test_client.post("/set_sheet_id", data="example")
#     if is_valid:
#         assert response.status_code == 200
#         assert response.text == "Sheet exists and is accessible"
#     else:
#         assert response.status_code == 409
#         assert response.text == "Access denied: The given ID does not match to any Google Sheets file"