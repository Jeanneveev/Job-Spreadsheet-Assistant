# import pytest
# import logging
# from flask.testing import FlaskClient   #for type hint
# from pytest_mock import MockerFixture   #for type hints
# from app.models import LinkedList, Node, Question
# from tests.helpers import generate_node, generate_question, build_test_ll
# import app.routes.blueprints.answer_form as answer_form

# def test_get_first_a_type_returns_a_type_value(test_client: FlaskClient, mocker:MockerFixture):
#     head = generate_node(generate_question(q_detail="first", a_type="preset"))
#     second = generate_node(generate_question(q_detail="second", a_type="preset"))
#     third = generate_node(generate_question(q_detail="third", a_type="open-ended"))

#     ll = build_test_ll(test_client, [head, second, third])

#     spy = mocker.spy(answer_form, "get_first_non_preset_node")

#     response = test_client.get("/get_first_a_type")
#     assert response.status_code == 200
#     result = response.text
#     assert result == "open-ended"
#     spy.assert_called_once()
# def test_get_first_a_type_returns_202_if_none(test_client: FlaskClient, mocker:MockerFixture):
#     head = generate_node(generate_question(q_detail="first", a_type="preset"))
#     second = generate_node(generate_question(q_detail="second", a_type="preset"))
#     build_test_ll(test_client, [head, second])

#     spy = mocker.spy(answer_form, "get_first_non_preset_node")

#     response = test_client.get("/get_first_a_type")
#     assert response.status_code == 404
#     result = response.text
#     assert result == "Please add at least one non-preset question"
#     spy.assert_called_once()

# class TestDisplayInfo():
#     @pytest.mark.parametrize("is_last", [True, False])  #ensure that it works both if and if not first question == last question
#     def test_get_first_question_returns_question_display_info(self, test_client:FlaskClient, mocker:MockerFixture, is_last):
#         # add test question(s) and node(s) to test ll
#         first_question = generate_question(q_str="Enter job name")
#         first_node = generate_node(first_question)
#         nodes = [first_node]
#         if not is_last:
#             next_question = generate_question(q_detail="next", a_type="multiple-choice")
#             next_node = generate_node(next_question)
#             nodes.append(next_node)
        
#         build_test_ll(test_client, nodes)

#         mocker.patch("app.routes.blueprints.answer_form.get_first_non_preset_node", return_value=first_node)
#         mocker.patch("app.routes.blueprints.answer_form.answer_leading_presets")

#         spy = mocker.spy(answer_form, "get_current_question_display_info")

#         response = test_client.get("/get_first_question")
#         assert response.status_code == 200

#         result = response.get_json()
#         if is_last:
#             expected = {
#                 "q_str": "Enter job name",
#                 "is_last": str(is_last).lower()
#             }
#         else:
#             expected = {
#                 "q_str": "Enter job name",
#                 "next_question_a_type": "multiple-choice",
#                 "is_last": str(is_last).lower()
#             }
#         assert result == expected
#         spy.assert_called_once_with(first_node, first_question)

#     @pytest.mark.parametrize("next_is_last, next_is_addon", [(True, True), (True, False), (False, True), (False, False)])
#     def test_get_next_question_returns_question_display_info(self, test_client:FlaskClient, test_session, mocker:MockerFixture, next_is_last, next_is_addon):        
#         nodes = []
#         # add nodes to ll
#         curr_q:Question = generate_question(q_str="q1", q_detail="1")
#         next_q = generate_question(q_str="q2", q_detail="2")
#         if next_is_addon:
#             curr_node:Node = generate_node(curr_q, next_q)
#             nodes.append(curr_node)
#         else:
#             curr_node:Node = generate_node(curr_q)
#             next_node:Node = generate_node(next_q)
#             nodes.extend([curr_node, next_node])
#         if not next_is_last:
#             last_node:Node = generate_node(generate_question(q_str="q3", q_detail="3", a_type="open-ended"))
#             nodes.append(last_node)
#         build_test_ll(test_client, nodes)

#         # set up session variables
#         sess_vars = {"curr_node": curr_node.as_dict(), "curr_question": curr_q.as_dict()}
#         test_session(test_client, sess_vars)

#         response = test_client.get("/get_next_question")
#         assert response.status_code == 200
#         expected = {
#             "q_str": "q2",
#             "is_last": str(next_is_last).lower(),
#             "is_addon": str(next_is_addon).lower()
#         }
#         if not next_is_last:
#             expected["next_question_a_type"] = "open-ended"
#         result = response.get_json()
#         assert result == expected
    
#     @pytest.mark.parametrize("prev_is_first, prev_is_addon", [(True, False), (False, True), (False, False)])
#     def test_get_prev_question_returns_question_display_info(self, test_client: FlaskClient, test_session, mocker:MockerFixture, prev_is_first, prev_is_addon):
#         nodes = []
#         # add nodes to ll
#         curr_q:Question = generate_question(q_str="current question", q_detail="curr", a_type="preset")
#         prev_q:Question = generate_question(q_str="previous question", q_detail="prev")
#         curr_node:Node = generate_node(curr_q)
#         if prev_is_addon:
#             prev_node:Node = generate_node(addon=prev_q)
#         else:
#             prev_node = generate_node(question=prev_q)
#         nodes.extend([prev_node, curr_node])
        
#         if not prev_is_first:
#             first_node:Node = generate_node()
#             nodes.insert(0, first_node)
#         build_test_ll(test_client, nodes)

#         # set up session variables
#         sess_vars = {"curr_node": curr_node.as_dict(), "curr_question": curr_q.as_dict()}
#         test_session(test_client, sess_vars)

#         response = test_client.get("/get_prev_question")
#         assert response.status_code == 200
#         expected = {
#             "q_str": "previous question",
#             "next_question_a_type": "preset",
#             "is_first": str(prev_is_first).lower(),
#             "is_addon": str(prev_is_addon).lower()
#         }
#         result = response.get_json()
#         assert result == expected


# class TestAnswers:
#     def test_set_answer_adds_answer_to_current_node(self, test_client:FlaskClient, test_session, caplog):
#         node:Node = generate_node(generate_question())
#         build_test_ll(test_client, [node])
#         sess_var = {"curr_node": node.as_dict()}
#         test_session(test_client, sess_var)

#         with caplog.at_level(logging.INFO):
#             response = test_client.post("/set_answer", data="test answer")
#         assert response.status_code == 200
#         assert response.text == "Answer test answer set"
#         assert node.answer == "test answer"
#         assert "Answer test answer set" in caplog.text


#     def test_add_addon_answer_appends_to_preexisting_answer(self, test_client:FlaskClient, test_session):
#         node:Node = generate_node(generate_question())
#         node.answer = "base"
#         build_test_ll(test_client, [node])
#         sess_var = {"curr_node": node.as_dict()}
#         test_session(test_client, sess_var)

#         response = test_client.post("/add_addon_answer", data="addon answer")
#         assert response.status_code == 200
#         assert response.text == 'Answer appended to. Answer is now "base (addon answer)"'

#     @pytest.mark.parametrize("valid_entry", [True, False])
#     def test_set_preset_answer_sets_only_existing_preset_types(self, test_client:FlaskClient, test_session, valid_entry):
#         node:Node = generate_node(generate_question())
#         build_test_ll(test_client, [node])
#         sess_var = {"curr_node": node.as_dict()}
#         test_session(test_client, sess_var)

#         if valid_entry:
#            response = test_client.post("/set_preset_answer", json={"preset_type": "empty"})
#            assert response.status_code == 200
#            assert node.answer == " "
#         else:
#             response = test_client.post("/set_preset_answer", json={"preset_type": "invalid"})
#             assert response.status_code == 404
#             assert node.answer == None

#     def test_get_answer_options_returns_options_if_any(self, test_client:FlaskClient, test_session):
#         node:Node = generate_node(generate_question())
#         node.question.options == ["first opt", "second opt", "third opt"]
#         build_test_ll(test_client, [node])
#         sess_var = {"curr_node": node.as_dict(), "curr_question": node.question.as_dict()}
#         test_session(test_client, sess_var)

#         response = test_client.get("/get_answer_options")
#         assert response.status_code == 200
#         assert response.get_json() == node.question.options

#     def test_get_all_answers_gets_all_answers(self, test_client:FlaskClient):
#         first_q:Question = generate_question(q_detail="first")
#         second_q:Question = generate_question(q_detail="second")
#         first_node:Node = generate_node(first_q)
#         second_node:Node = generate_node(second_q)
#         first_node.answer = "answer 1"
#         second_node.answer = "answer 2"
#         build_test_ll(test_client, nodes=[first_node, second_node])

#         response = test_client.get("/get_all_answers")
#         assert response.status_code == 200
#         assert response.get_json() == ["answer 1", "answer 2"]

