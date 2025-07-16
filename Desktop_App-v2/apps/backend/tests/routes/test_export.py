import pytest
from flask.testing import FlaskClient   #for type hint
from ..helpers import build_test_export_data

def test_set_export_method_can_set_export_data_method(test_client):
    ...