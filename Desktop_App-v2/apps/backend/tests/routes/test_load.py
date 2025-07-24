import pytest
import io
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hint
from tests.helpers import generate_node, generate_question, build_test_ll, set_test_config
from app.services.load import *
import app.services.load as load

class TestUploadFile:
    def test_upload_file_cannot_upload_nonexistent_file(self, test_client:FlaskClient):
        # no file requested
        response_1 = test_client.post("/upload_file")
        assert response_1.status_code == 404
        assert response_1.text == "ERROR: No file in request"

        # clicked upload without selecting a file
        empty_file = {"file": (io.BytesIO(b""), "")}
        response_2 = test_client.post("/upload_file", data=empty_file, content_type="multipart/form-data")
        assert response_2.status_code == 404
        assert response_2.text == "ERROR: No file selected"
        
    def test_upload_file_cannot_upload_wrong_file_type(self, test_client:FlaskClient):
        wrong_filetype = {"file": (io.BytesIO(b"test content"), "wrong_type.txt")}
        response = test_client.post("/upload_file", data=wrong_filetype, content_type="multipart/form-data")
        assert response.status_code == 409
        assert response.text == "ERROR: Wrong file type"

    def test_upload_file_cannot_upload_wrong_file_format(self, test_client:FlaskClient):
        wrong_content = '[{"test": "wrong value"}]'
        data = {"file": (io.BytesIO(wrong_content.encode("utf-8")), "badfile.json")}
        response = test_client.post("/upload_file", data=data, content_type="multipart/form-data")
        assert response.status_code == 409
        assert response.text == "ERROR: Wrong file format"
        
    def test_upload_file_can_upload_valid_file(self, test_client:FlaskClient):
        # create old ll to be overwritten
        old_node:Node = generate_node(generate_question())
        _ = build_test_ll(test_client, [old_node])
        
        content = '''
            [{
                "question": {
                    "q_str": "test name",
                    "q_detail": "test detail",
                    "q_type": "singular",
                    "a_type": "open-ended"
                },
                "addon": {
                    "q_str": "addon name",
                    "q_detail": "addon detail",
                    "q_type": "add-on",
                    "a_type": "multiple-choice",
                    "options": [
                        "1",
                        "2",
                        "3"
                    ]
                }
            }]
        '''
        data = {"file": (io.BytesIO(content.encode("utf-8")), "valid_file.json")}
        response = test_client.post("/upload_file", data=data, content_type="multipart/form-data")

        assert response.status_code == 200
        expected = ["test detail", "addon detail"]
        assert response.text == f"File saved. Loaded questions: {expected}"

def test_get_working_qg_info_can_get_working_qg_info(test_client:FlaskClient):
    question_1:Question = generate_question(q_detail="1")
    question_2:Question = generate_question(q_detail="+1")
    question_3:Question = generate_question(q_detail="2")
    node_1:Node = generate_node(question=question_1, addon=question_2)
    node_2:Node = generate_node(question_3)
    _ = build_test_ll(test_client, [node_1, node_2])
    
    response = test_client.get("/get_working_qg_info")
    assert response.status_code == 200

    expected_name = "Working QG"
    expected_date = datetime.today().strftime("%m/%d/%Y")
    expected_num_q = 3
    expected = {"display_info": [expected_name, expected_date, expected_num_q]}
    assert response.get_json() == expected

def test_load_all_files_can_get_file_display_info(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    valid_1 = test_upload_folder / "qg_valid.json"
    valid_2 = test_upload_folder / "qg_valid_2.json"
    invalid_1 = test_upload_folder / "not_qg.json"
    invalid_2 = test_upload_folder / "qg_invalid_format.json"
    test_upload_folder.mkdir()
    valid_1.touch()
    valid_2.touch()
    invalid_1.touch()
    invalid_2.touch()
    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    valid_data = [
        {"question": {
            "q_str": "test q",
            "q_detail": "1",
            "q_type": "singular",
            "a_type": "open-ended"
        }},
        {"question": {
            "q_str": "test q 2",
            "q_detail": "2",
            "q_type": "singular",
            "a_type": "open-ended"
        }},
    ]
    invalid_data = [{"invalid": "Invalid"}]
    valid_1.write_text(json.dumps(valid_data, indent=4), encoding="utf-8")
    valid_2.write_text(json.dumps(valid_data, indent=4), encoding="utf-8")
    invalid_2.write_text(json.dumps(invalid_data, indent=4), encoding="utf-8")

    expected_time = time.strftime("%m/%d/%Y", time.gmtime(os.path.getmtime(str(valid_1))))
    expected_result = [["valid_2", expected_time, 2], ["valid", expected_time, 2]]
    
    response = test_client.get("/load_all_files")
    assert response.status_code == 200
    result = response.get_json()["files_display_info"]
    assert sorted(result) == sorted(expected_result)

def test_update_selected_qg_can_switch_linked_list(test_client:FlaskClient, mocker, tmp_path):
    # Build old ll
    question_1:Question = generate_question(q_detail="1")
    question_2:Question = generate_question(q_detail="+1")
    question_3:Question = generate_question(q_detail="2")
    node_1:Node = generate_node(question=question_1, addon=question_2)
    node_2:Node = generate_node(question_3)
    _ = build_test_ll(test_client, [node_1, node_2])

    # Build upload file and folder
    name = "test"
    test_upload_folder = tmp_path / "upload"
    valid = test_upload_folder / f"qg_{name}.json"
    test_upload_folder.mkdir()
    valid.touch()
    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    valid_data = [
        {"question": {
            "q_str": "test q",
            "q_detail": "1",
            "q_type": "singular",
            "a_type": "open-ended"
        }},
        {"question": {
            "q_str": "test q 2",
            "q_detail": "2",
            "q_type": "singular",
            "a_type": "open-ended"
        }},
    ]
    valid.write_text(json.dumps(valid_data, indent=4), encoding="utf-8")

    response = test_client.post("/update_selected_qg", data=name)
    assert response.status_code == 200

