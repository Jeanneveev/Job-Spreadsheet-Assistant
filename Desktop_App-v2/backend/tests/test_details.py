from flask.testing import FlaskClient   #for type hint
import json

class TestAddDetail:
    def test_add_one_detail_to_list(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/add_detail' route is requested with the
        'POST' method and a detail is being added for the first time
        THEN check that the response is a list with only that detail
        """
        response = test_client.post("/add_detail", data="test1")
        assert response.status_code == 200
        print("singular response is",json.loads(response.data))
        res = json.loads(response.data)["result"]
        assert json.loads(res) == ["test1"]

    def test_add_multiple_details_to_list(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/add_detail' route is requested with the
        'POST' method multiple times
        THEN check that the response is a list with the passed details
        """
        test_client.delete("/clear_details")    #clear the session variable
        response = test_client.post("/add_detail", data="test")
        response = test_client.post("/add_detail", data="1")
        response = test_client.post("/add_detail", data="!")
        assert response.status_code == 200
        print("mult response is: ",json.loads(response.data))
        res = json.loads(response.data)["result"]
        assert json.loads(res) == ["test","1","!"]

    def test_add_detail_with_whitespace(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/add_detail' route is requested with the
        'POST' method and a detail containing whitespace is passed
        THEN check that the response is a list with the passed detail,
        whitespace included
        """
        test_client.delete("/clear_details")    #clear the session variable
        response = test_client.post("/add_detail", data="testing ")
        response = test_client.post("/add_detail", data=" test ")
        response = test_client.post("/add_detail", data=" tested")
        assert response.status_code == 200
        res = json.loads(response.data)["result"]
        assert json.loads(res) == ["testing "," test "," tested"]

    def test_add_empty_detail_to_list(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/add_detail' route is requested with the
        'POST' method and nothing is passed to its URL parameter
        THEN check that the response's status code is 404
        """
        response = test_client.post("/add_detail", data="")
        assert response.status_code == 404

    def test_add_detail_to_list_wrong_method(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/add_detail' route is requested with the
        'GET' method
        THEN check that the response's status code is 405
        """
        response = test_client.get("/add_detail", data="test")
        assert response.status_code == 405

class TestDeleteDetail:
    def test_delete_only_detail(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/delete_detail' route is requested with the
        'DELETE' method and the passed detail is the only detail
        existing within the 'detail_lst' session variable
        THEN check that the response is a confirmation message showing
        that 'detail_lst' is now an empty list
        """
        test_client.delete("/clear_details")    #clear the session variable
        response_add = test_client.post("/add_detail", data="test")
        print("added detail. Details are:",json.loads(response_add.data))
        assert json.loads(json.loads(response_add.data)["result"]) == ["test"]
        
        response = test_client.delete("/delete_detail", data="test")
        assert response.status_code == 200
        assert response.content_type == "text/html; charset=utf-8"
        res = response.data.decode("utf-8")
        print("deleted detail. Details is now:",res)
        assert res == "Detail test deleted. Detail_lst is now: []"

    def test_delete_one_of_many_details(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/delete_detail' route is requested with the
        'DELETE' method and the passed detail is one of many details
        existing within the 'detail_lst' session variable
        THEN check that the response is a confirmation message showing
        that 'detail_lst' is now None
        """
        test_client.delete("/clear_details")    #clear the session variable
        test_client.post("/add_detail", data="test1")
        test_client.post("/add_detail", data="test2")
        test_client.post("/add_detail", data="test3")
        response_add = test_client.post("/add_detail", data="test4")
        res_add = json.loads(json.loads(response_add.data)["result"])
        assert res_add == ["test1","test2","test3","test4"]

        response = test_client.delete("/delete_detail", data="test2")
        assert response.status_code == 200
        assert response.content_type == "text/html; charset=utf-8"
        res:str = response.data.decode("utf-8")
        res = res.split(": ")[1]   #get only the list
        result:list[str] = json.loads(res)
        assert result == ["test1", "test3", "test4"]

    def test_delete_nonexisting_detail(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/delete_detail' route is requested with the
        'DELETE' method and the passed detail does not exist within
        the 'detail_lst' session variable
        THEN check that the response is a custom error message with a
        status code of 404
        """
        test_client.delete("/clear_details")    #clear the session variable
        response_add = test_client.post("/add_detail", data="test1")
        res_add = json.loads(json.loads(response_add.data)["result"])
        assert res_add == ["test1"]

        response = test_client.delete("/delete_detail", data="test2")
        assert response.status_code == 400
        assert response.content_type == "text/html; charset=utf-8"
        res:str = response.data.decode("utf-8")
        assert res == "Detail is not in detail_lst"

    def test_delete_no_detail(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/delete_detail' route is requested with the
        'DELETE' method and the passed detail is nothing
        THEN check that the response is the default error message with
        a status code of 404
        """
        test_client.delete("/clear_details")    #clear the session variable
        
        response = test_client.delete("/delete_detail", data="test2")
        assert response.status_code == 404
        assert response.content_type == "text/html; charset=utf-8"
        res:str = response.data.decode("utf-8")
        assert res == "No details to delete"
        
    def test_delete_detail_wrong_method(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/delete_detail' route is requested with the
        'GET' method
        THEN check that the response's status code is 405
        """
        test_client.delete("/clear_details")    #clear the session variable
        response_add = test_client.post("/add_detail", data="test1")
        res_add = json.loads(json.loads(response_add.data)["result"])
        assert res_add == ["test1"]

        response = test_client.get("/delete_detail", data="test1")
        assert response.status_code == 405

class TestClearDetails:
    def test_clear_no_details(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/clear_detail' route is requested with the
        'DELETE' method while there is no details in
        the 'detail_lst' session variable
        THEN check that the response shows that all details were
        cleared
        """
        response = test_client.delete("/clear_details")
        assert response.status_code == 200
        assert response.content_type == "text/html; charset=utf-8"
        res_text:str = response.data.decode("utf-8")
        res_lst:list[str] = json.loads(res_text.split(": ")[1])
        assert res_text == "Any if all details deleted. Detail_lst is now: []"
        assert res_lst == []
    def test_clear_some_details(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/clear_detail' route is requested with the
        'DELETE' method while there is at least one detail in
        the 'detail_lst' session variable
        THEN check that the response shows that all details were
        cleared
        """
        pass
    def test_clear_detail_wrong_method(self, test_client: FlaskClient):
        """
        GIVEN a Flask app configured for testing
        WHEN the '/clear_detail' route is requested with the
        'DELETE' method
        THEN check that the response's status code is 405
        """
        pass

# class TestGetDetails:
#     def test_get_one_detail(self, test_client: FlaskClient):
#         pass
#     def test_get_multiple_details(self, test_client: FlaskClient):
#         pass
#     def test_get_no_details(self, test_client: FlaskClient):
#         pass
#     def test_get_details_wrong_method(self, test_client: FlaskClient):
#         pass

# class TestGetBaseDetails:
#     def test_get_one_base_detail(self, test_client: FlaskClient):
#         pass
#     def test_get_multiple_base_details(self, test_client: FlaskClient):
#         pass
#     def test_get_no_base_details(self, test_client: FlaskClient):
#         pass
#     def test_get_base_details_wrong_method(self, test_client: FlaskClient):
#         pass

# class TestCheckDetail:
#     def test_check_existing_detail(self, test_client: FlaskClient):
#         pass
#     def test_check_nonexisting_detail(self, test_client: FlaskClient):
#         pass
#     def test_check_deleted_detail(self, test_client: FlaskClient):
#         pass
#     def test_check_detail_wrong_method(self, test_client: FlaskClient):
#         pass