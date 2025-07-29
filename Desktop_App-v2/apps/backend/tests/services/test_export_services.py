import pytest
import pandas
import numpy as np
from flask.testing import FlaskClient   #for type hint
from werkzeug.datastructures import FileStorage
from ..helpers import (build_test_export_data, set_test_config,
    generate_node, generate_question, build_test_ll
)
from app.services.export import *

def test_set_export_method_cannot_set_invalid_method(test_client:FlaskClient):
    invalid_method = "json"
    build_test_export_data(test_client)

    with pytest.raises(ValueError, match="Invalid method value"):
        set_export_method(invalid_method)

def test_set_export_method_can_set_valid_method(test_client:FlaskClient):
    valid_method = "sheets"
    build_test_export_data(test_client)
    
    assert set_export_method(valid_method) == valid_method

def test_set_new_export_csv_cannot_set_to_existing_file(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    existing_csv = test_export_folder / "test.csv"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()
    existing_csv.touch()

    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    name = "test"
    
    with pytest.raises(FileExistsError, match=f'CSV {name} already exists'):
        _ = set_new_export_csv({"new_csv_name": name})

def test_set_new_export_csv_can_set_to_new_file(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()

    form_data = {"new_csv_name": "name"}

    result = set_new_export_csv(form_data)
    # NOTE: It seems like the test name gets cut off at differing points,
    # so we can't compare the whole path string
    assert "\\upload\\exports\\name.csv" in result

def test_set_old_export_csv_cannot_set_nonexistent_files():
    with pytest.raises(FileNotFoundError, match="ERROR: No file in request"):
        set_old_export_csv({})

    with pytest.raises(FileNotFoundError, match="ERROR: No file selected"):
        file = FileStorage(filename="")
        set_old_export_csv({"file": file})

def test_set_old_export_csv_can_set_to_existing_files(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    existing_csv = test_export_folder / "test.csv"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()
    existing_csv.touch()

    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    filename = "test.csv"
    file = FileStorage(filename=filename)

    result = set_old_export_csv({"file": file})
    assert "\\upload\\exports\\test.csv" in result

def test_set_old_export_csv_can_set_to_new_files(test_client:FlaskClient, tmp_path):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()

    config_params = {"UPLOAD_FOLDER": test_upload_folder}
    set_test_config(test_client, config_params)

    filename = "test.csv"
    file = FileStorage(filename=filename)

    result = set_old_export_csv({"file": file})
    assert "\\upload\\exports\\test.csv" in result
    
def test_get_csv_headers_can_get_existing_headers():
    df = pandas.DataFrame(columns=["1", "2", "3"])
    assert get_csv_headers(df) == ["1", "2", "3"]

def test_get_csv_headers_can_get_q_details_as_headers(test_client:FlaskClient):
    node_1 = generate_node(generate_question(q_detail="1"), generate_question(q_detail="+1"))
    node_2 = generate_node(generate_question(q_detail="2"))
    node_3 = generate_node(generate_question(q_detail="4"))
    _ = build_test_ll(test_client, [node_1, node_2, node_3])

    df = pandas.DataFrame()
    assert get_csv_headers(df) == ["1", "2", "4"]

def test_export_data_to_csv_can_append_equal_lengths_of_data_to_existing_csv(test_client:FlaskClient, tmp_path, mocker):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    existing_csv = test_export_folder / "test.csv"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()
    existing_csv.touch()

    existing_df = pandas.DataFrame([["a", "b", "c"]], columns=["1", "2", "3"])
    existing_df.to_csv(existing_csv, index=False)

    data = ["A", "B", "C"]
    build_test_export_data(test_client, {"loc": existing_csv, "data": data})

    spy = mocker.spy(pandas, "concat")
    _ = export_data_to_csv()

    expected = pandas.DataFrame([["a", "b", "c"], ["A", "B", "C"]], columns=["1", "2", "3"])
    assert spy.spy_return.equals(expected)

def test_export_data_to_csv_can_append_shorter_data_to_existing_csv(test_client:FlaskClient, tmp_path, mocker):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    existing_csv = test_export_folder / "test.csv"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()
    existing_csv.touch()

    existing_df = pandas.DataFrame([["a", "b", "c"]], columns=["1", "2", "3"])
    existing_df.to_csv(existing_csv, index=False)

    data = ["A", "B"]
    build_test_export_data(test_client, {"loc": existing_csv, "data": data})

    spy = mocker.spy(pandas, "concat")
    _ = export_data_to_csv()

    expected = pandas.DataFrame([["a", "b", "c"], ["A", "B", ""]], columns=["1", "2", "3"])
    assert spy.spy_return.equals(expected)

def test_export_data_to_csv_can_append_shortened_longer_data_to_existing_csv(test_client:FlaskClient, tmp_path, mocker):
    test_upload_folder = tmp_path / "upload"
    test_export_folder = test_upload_folder / "exports"
    existing_csv = test_export_folder / "test.csv"
    test_upload_folder.mkdir()
    test_export_folder.mkdir()
    existing_csv.touch()

    existing_df = pandas.DataFrame([["a", "b", "c"]], columns=["1", "2", "3"])
    existing_df.to_csv(existing_csv, index=False)

    data = ["A", "B", "C", "D"]
    build_test_export_data(test_client, {"loc": existing_csv, "data": data})

    spy = mocker.spy(pandas, "concat")
    _ = export_data_to_csv()

    expected = pandas.DataFrame([["a", "b", "c"], ["A", "B", "C"]], columns=["1", "2", "3"])
    assert spy.spy_return.equals(expected)