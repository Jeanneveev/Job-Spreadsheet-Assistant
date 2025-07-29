import pytest
from flask.testing import FlaskClient   #for type hint
from tests.helpers import generate_node, generate_question, build_test_ll, set_test_config
from app.services.load import *

@pytest.mark.parametrize("is_allowed", [True, False])
def test_check_allowed_extension_only_allows_json_extensions(is_allowed):
    if is_allowed:
        file = "valid.json"
    else:
        file = "invalid.txt"

    assert check_allowed_extension_json(file) == is_allowed

def test_validate_upload_cannot_validate_incorrectly_formatted_json():
    invalid_json = [{"invalid": "Invalid"}]
    assert validate_upload(invalid_json) == False

def test_validate_upload_can_validate_correctly_formatted_json():
    valid_json = [{
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
    assert validate_upload(valid_json) == True

def test_load_details_can_get_question_q_detail(test_client:FlaskClient, test_session):
    test_json:list[dict] = [
        {"question": {"q_detail": "1"}, "addon": {"q_detail": "+1"}},
        {"question": {"q_detail": "2"}},
        {"question": {"q_detail": "4"}}
    ]
    sess_var = {"all_details": ["to be cleared"]}
    test_session(test_client, sess_var)
    test_client.get("/")    # throwaway call to establish session

    assert load_details(test_json) == ["1", "+1", "2", "4"]

def test_load_ll_can_load_new_linked_list(test_client:FlaskClient):
    old_node:Node = generate_node(generate_question())
    old_ll:LinkedList = build_test_ll(test_client, [old_node])
    loaded_new_ll = [
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
    
    assert load_ll(old_ll, loaded_new_ll).getAll() == loaded_new_ll

def test_load_ll_and_details_can_get_new_linked_list_and_q_details(test_client:FlaskClient, test_session):
    old_node:Node = generate_node(generate_question(q_detail="0"))
    old_ll:LinkedList = build_test_ll(test_client, [old_node])
    loaded_new_ll = [
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

    sess_var = {"all_details": ["0"]}
    test_session(test_client, sess_var)
    test_client.get("/")    # throwaway call to establish session

    expected = ["1", "2"]
    assert load_ll_and_details(old_ll, loaded_new_ll) == f"Loaded questions: {expected}"

def test_get_working_info_returns_display_info(test_client:FlaskClient):
    question_1:Question = generate_question(q_detail="1")
    question_2:Question = generate_question(q_detail="+1")
    question_3:Question = generate_question(q_detail="2")
    node_1:Node = generate_node(question=question_1, addon=question_2)
    node_2:Node = generate_node(question_3)
    ll = build_test_ll(test_client, [node_1, node_2])

    expected_name = "Working QG"
    expected_date = datetime.today().strftime("%m/%d/%Y")
    expected_num_q = 3
    assert get_working_qg_info(ll) == [expected_name, expected_date, expected_num_q]

def test_get_all_valid_files_can_identify_all_valid_files(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    valid = test_upload_folder / "qg_valid.json"
    invalid_1 = test_upload_folder / "not_qg.json"
    invalid_2 = test_upload_folder / "qg_invalid_format.json"
    test_upload_folder.mkdir()
    valid.touch()
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
    valid.write_text(json.dumps(valid_data, indent=4), encoding="utf-8")
    invalid_2.write_text(json.dumps(invalid_data, indent=4), encoding="utf-8")

    assert get_all_valid_file_paths() == [str(tmp_path / "upload" / "qg_valid.json")]

def test_get_loaded_num_questions_can_count_all_questions():
    data = [
        {"question": {"q_detail": "1"}, "addon": {"q_detail": "+1"}},
        {"question": {"q_detail": "2"}},
        {"question": {"q_detail": "3"}}
    ]

    assert get_loaded_num_questions(data) == 4

def test_get_files_display_info(test_client:FlaskClient, tmp_path):
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
    expected = [["valid_2", expected_time, 2], ["valid", expected_time, 2]]
    actual = list(get_files_display_info())
    assert sorted(actual) == sorted(expected)