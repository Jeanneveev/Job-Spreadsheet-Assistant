import pytest
from flask.testing import FlaskClient   #for type hint
from app.services.details import *

class TestAddDetail:
    def add_detail_to_all_details_cannot_add_empty_detail(self):
        with pytest.raises(ValueError, msg="Empty detail was passed"):
            new_detail = ""
            add_detail_to_all_details(new_detail)

    def add_detail_to_all_details_cannot_add_existing_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2"]
        new_detail = "1"

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)
        test_client.get("/")    #cursory call to set up session

        with pytest.raises(ValueError, msg="This detail already exists"):
            add_detail_to_all_details(new_detail)

    def add_detail_can_add_new_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2"]
        new_detail = "3"
        expected = ["1", "2", "3"]

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)
        test_client.get("/")    #cursory call to set up session

        assert add_detail_to_all_details(new_detail) == expected

class DeleteDetail:
    def test_remove_detail_from_all_details_cannot_remove_empty_detail(self):
        with pytest.raises(ValueError, msg="Empty detail was passed"):
            new_detail = ""
            remove_detail_from_all_details(new_detail)

    def test_remove_detail_from_all_details_cannot_remove_nonexistent_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2"]
        new_detail = "3"

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)
        test_client.get("/")    #cursory call to set up session

        with pytest.raises(ValueError, msg="This detail does not exists"):
            remove_detail_from_all_details(new_detail)

    def test_remove_detail_from_all_details_can_remove_existing_detail(self, test_client:FlaskClient, test_session):
        existing_details = ["1", "2", "3"]
        new_detail = "2"
        expected = ["1", "3"]

        sess_var = {"all_details": existing_details}
        test_session(test_client, sess_var)
        test_client.get("/")    #cursory call to set up session

        assert remove_detail_from_all_details(new_detail) == expected