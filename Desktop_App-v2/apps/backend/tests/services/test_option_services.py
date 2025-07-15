import pytest
from flask.testing import FlaskClient   #for type hint
from pytest_mock import MockerFixture   #for type hint
from app.models import Question, Node
from tests.helpers import generate_node, generate_question, build_test_ll
import app.services.options as options_service
from app.services.options import *


def test_add_options_to_question_returns_only_unique_values(test_client:FlaskClient, mocker:MockerFixture):
    question:Question = generate_question()
    existing_options:list[str] = ["example opt 1", "example opt 2"]
    question.options = existing_options
    mocker.patch("app.services.options.get_current_question", return_value=question)

    new_options = ["example opt 1", "example opt 3"]
    test_client.get("/")    # throwaway call to establish session
    assert add_options_to_question(new_options) == ["example opt 1", "example opt 2", "example opt 3"]
    assert question.options == ["example opt 1", "example opt 2", "example opt 3"]

def test_add_new_options_to_all_options_returns_only_unique_values(test_client:FlaskClient, test_session):
    existing_options:list[str] = ["opt 1", "opt 2"]
    test_session(test_client, {"all_options": existing_options})

    new_options = ["opt 2", "opt 3", "opt 5"]
    test_client.get("/")    # throwaway call to establish session
    assert add_new_options_to_all_options(new_options) == ["opt 1", "opt 2", "opt 3", "opt 5"]

