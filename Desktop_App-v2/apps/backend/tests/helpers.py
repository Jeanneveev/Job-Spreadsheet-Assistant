from pathlib import Path
from flask.testing import FlaskClient   #for type hints
from app.models import QTypeOptions, ATypeOptions, Question, Node, LinkedList, ExportData

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
    """Builds a LinkedList in the test client's app context, allowing it to be interacted
        with by functions being tested.

        Parameters:
            test_client: FlaskClient - The tester Flask app's Flask client
            nodes: list[Node] - A list of nodes, in order, to be added to the linked list
    """
    app = test_client.application  # The Flask app instance
    with app.app_context():
        app.linked_list = LinkedList()
        
        for node in nodes:
            app.linked_list.append(node)
        
        return app.linked_list

def build_test_export_data(test_client:FlaskClient, args:dict=None):
    app = test_client.application  # The Flask app instance
    # export_params = ["data", "method", "service", "loc", "sheet_id"]
    with app.app_context():
        app.export_data = ExportData()
        # add arguments if any
        if args:
            for k, v in args.items():
                match k:
                    case "data":
                        app.export_data.data = v
                        break
                    case "method":
                        app.export_data.method = v
                        break
                    case "service":
                        app.export_data.service = v
                        break
                    case "loc":
                        app.export_data.loc = v
                        break
                    case "sheet_id":
                        app.export_data.sheet_id = v
                        break
                    case _:
                        break

def set_test_config(test_client:FlaskClient, config_params:dict):
    app = test_client.application  # The Flask app instance
    with app.app_context():
        for k, v in config_params.items():
            app.config[k] = v

def get_test_upload_folder():
    return str(Path(__file__).parent / "upload")