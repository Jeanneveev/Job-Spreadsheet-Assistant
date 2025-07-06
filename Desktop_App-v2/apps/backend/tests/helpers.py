from flask.testing import FlaskClient   #for type hints
from app.models import QTypeOptions, ATypeOptions, Question, Node, LinkedList

def generate_question(q_str="test", q_detail="test", q_type="singular", a_type="open-ended") -> Question:
    return Question(
        q_str = q_str,
        q_detail = q_detail,
        q_type = QTypeOptions(q_type),
        a_type = ATypeOptions(a_type)
    )
def generate_node(question:Question=None, addon:Question=None) -> Node:
    q = question if question is not None else generate_question()
    a = addon if addon is not None else None
    if addon:
        return Node(question=q, addon=a)
    else:
        return Node(q)
    
def build_test_ll(test_client:FlaskClient, nodes:list[Node]):
    app = test_client.application  # The Flask app instance
    with app.app_context():
        app.linked_list = LinkedList()
        
        for node in nodes:
            app.linked_list.append(node)