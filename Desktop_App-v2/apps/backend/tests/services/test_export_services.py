import pytest
from flask.testing import FlaskClient   #for type hint
from ..helpers import build_test_export_data
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