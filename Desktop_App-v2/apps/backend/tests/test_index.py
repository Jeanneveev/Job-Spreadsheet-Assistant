from flask.testing import FlaskClient   #for type hint
import json

def test_home_page(test_client: FlaskClient):
    """
    GIVEN a Flask app configured for testing
    WHEN the '/' page is requested with the 'GET' method
    THEN check that the response is valid
    """
    response = test_client.get("/")
    print(f"response is: {response.data}")
    assert response.status_code == 200
    assert json.loads(response.data) == {"result":"Server active!"}
    assert json.loads(response.data)["result"] == "Server active!"