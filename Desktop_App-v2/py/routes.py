from enum import Enum

class QTypeOptions(Enum):
    SINGULAR="singular"
    BASE="base"
    ADD_ON="add-on"
class ATypeOptions(Enum):
    MULT="multiple-choice"
    TEXT="open-ended"
class Question:
    def __init__(self,q_str:str,q_detail:str,q_type:QTypeOptions,a_type:ATypeOptions)->None:
        self.q_str=q_str
        self.q_detail=q_detail
        self.q_type=q_type
        self.a_type=a_type
    def __str__(self)->str:
        return f"{self.q_detail}"
    def as_dict(self)->dict:
        return {"q_str":self.q_str,"q_detail":self.q_detail,
                "q_type":self.q_type.value,"a_type":self.a_type.value}
class Node:
    def __init__(self,question):
        self.question:Question=question
        self.addon:Question=None
        self.answer:str=None
        self.next:Node=None
    def __str__(self)->str:
        s=f"The Node is for the question \"{self.question.q_str}\""
        if self.addon:
            s+=f". This Node also has the addon question \"{self.addon.q_str}\""
        return s
    def as_dict(self)->dict:
        res_dict={"question":self.question.as_dict()}
        if self.addon:
            res_dict["addon"]=self.addon.as_dict()
        if self.answer:
            res_dict["answer"]=self.answer
        return res_dict
class LinkedList:
    def __init__(self):
        self.head:Node=None

    def append(self,node:Node)->None:
        if self.head is None:
            self.head=node
            return
        #traverse until the end of the linked list
        tail:Node=self.head
        while tail.next:
            tail=tail.next
        tail.next=node
    def printLL(self):
        curr=self.head
        while curr:
            print(curr.question,end="->")
            curr=curr.next
        print("null")
    def returnLL(self):
        curr=self.head
        res=""
        while curr:
            res+=f"{curr.question.q_detail}->"
            curr=curr.next
        res+="null"
        return res
    def getByQType(self,val:str)->list[str]:
        found:list[str]=[]
        curr:Node=self.head
        while curr:
            # print("loop started")
            if curr.question.q_type==QTypeOptions(val):
                # print("matched")
                found.append(curr.question.q_detail)
            curr=curr.next
        return found
    def getByDetail(self,val:str)->Node|None:
        curr:Node=self.head
        while curr:
            if curr.question.q_detail==val:
                print("matched")
                return curr
            curr=curr.next
        return None
    def getAll(self)->list[dict]:
        res=[]
        curr:Node=self.head
        while curr:
            res.append(curr.as_dict())
            curr=curr.next
        return res


# ROUTES
from flask import Flask, request, session, jsonify
from flask_session import Session
from flask_cors import CORS
import redis, json
#for clearing session files
import atexit

app = Flask(__name__)
app.config.from_object("config.Config")
redis_url = app.config.get("SESSION_REDIS") #getting SESSION_REDIS to check connection
def test_redis_connection(redis_session):
    """Check that Redis is connected to"""
    try:
        redis_session.ping()  # Check if Redis is alive
        print("Redis connection successful!")
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}")
        exit()  # Or handle the error appropriately
test_redis_connection(redis_url)

# Initialize Plugins
sess=Session()
sess.init_app(app)
CORS(app,supports_credentials=True)


ll=LinkedList() #initialize linked list to be used later

#check that the server's running and connected
@app.route("/", methods=["GET","POST"])
def check():
    # print("Working directory path is",os.getcwd(),". Current directory path is",os.path.dirname(os.path.abspath(sys.argv[0])))
    return {"result":"Server active!"}

## ADD QUESTIONS
@app.route("/add_question", methods=["POST"])
def add_question():
    """Make a new Question with the info passed"""
    result=request.form
    print(result)
    #all of the form sections are required, so we don't need to check for NULLs
    # however, we do need to check if base or add-on was selected because they're in their own group
    if "q_type_2" in result:
        q_type=QTypeOptions(result["q_type_2"])
    else:
        q_type=QTypeOptions(result["q_type"])
    a_type=ATypeOptions(result["a_type"])
    new_question=Question(result["question"],result["detail"],q_type,a_type)
    print("Created question:",new_question)
    new_node=Node(new_question)
    ll.append(new_node)
    ll.printLL()
    return {"response":"added question"}
@app.route("/add_question/addon", methods=["POST"])
def add_addon():
    result=request.form
    #make a question from the results
    q_type=QTypeOptions(result["q_type_2"])
    a_type=ATypeOptions(result["a_type"])
    new_question=Question(result["question"],result["detail"],q_type,a_type)
    #get the node of the question this one is adding onto
    base_detail=result["addon_to"]
    base_node=ll.getByDetail(base_detail)
    #set the base's addon value to the addon Question
    base_node.addon=new_question
    print(f"Addon \"{new_question.q_detail}\" added to base node \"{base_node.question.q_detail}\"")
    return {"response":"added addon question"}
## DETAILS
@app.route("/add_detail/<detail>",methods=["GET","POST"])
def add_detail_to_list(detail):
    """Add a q_detail to a list of q_details"""
    # Initialize the list if it doesn't exist
    if 'lst' not in session:
        print("Session variable not found. Initializing...")
        session['lst'] = json.dumps([])
        session.modified = True
    # Append to the list
    lst:list[str]=json.loads(session['lst'])
    print("Before appending:",lst)
    lst.append(detail)
    print("After appending:",lst)
    session['lst'] = json.dumps(lst)
    session.modified = True

    return {"response":f"{lst}"}
@app.route("/get_all_details",methods=["GET"])
def get_all_details():
    details:list[str]=session.get("lst",[])
    return {"result":details}
@app.route("/check_detail/<detail>")
def check_detail(detail):
    details:list[str]=session.get("lst",[])
    if detail in details:
        return {"result":"True","detail_list":details}
    else:
        return {"result":"False","detail_list":details}


@app.route("/get_all_base_details", methods=["GET"])
def get_all_base_details():
    """Get the details of all nodes with the q_type 'base'"""
    base_list=ll.getByQType("base")
    return {"result":base_list}
## VIEW
@app.route("/get_ll_json", methods=["GET"])
def all_to_json():
    """Get every node in the linked list and return them as json"""
    print(ll.getAll())
    return {"result":ll.getAll()}
## SAVE
import time
import os
@app.route("/save_file", methods=["GET"])
def write_ll_to_file():
    """Write all nodes of the linked list to a file"""
    ll_json:list[dict]=ll.getAll()
    #using the current time to make each save unique
    curr_time = time.strftime("%m%d%Y_%H%M%S", time.localtime())
    curr_dir=os.path.dirname(__file__)
    path=f"Saves/questions_{curr_time}.json"
    save_path=os.path.join(curr_dir, os.pardir, path)
    with open(save_path,"w+", encoding="utf-8") as file:
        json.dump(ll_json,file,ensure_ascii=False,indent=4)

    return {"result":f"Questions saved to {save_path}"}

## LOAD
#double-checking extensions since the "accepts" attribute can be bypassed
from jsonschema import validate
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS=[".json"]
def check_allowed_extension(filename):
    extension=os.path.splitext(filename)[1]
    # print(f"Extension is: {extension}")
    if extension in ALLOWED_EXTENSIONS:
        print("File's extension allowed")
        return True
    else:
        print("Incorrect file extension")
        return False
    
def validate_upload(file_json):
    """Given a JSON file, confirm that it's in the right format to be turned into a LinkedList object"""
    schema={
        "type":"object",
        "properties":{
            "question": {
                "type":"object",
                "properties": {
                    "q_str": {"type":"string"},
                    "q_detail": {"type":"string"},
                    "q_type": {"type":"string"},
                    "a_type": {"type":"string"}
                },
                "required":["q_str","q_detail","q_type","a_type"]
            },
            "addon":{
                "type":"object",
                "properties": {
                    "q_str": {"type":"string"},
                    "q_detail": {"type":"string"},
                    "q_type": {"type":"string"},
                    "a_type": {"type":"string"}
                },
                "required":["q_str","q_detail","q_type","a_type"]
            },
            "answer":{
                "type":"string"
            },
            "required":["question"]
        }
    }
    try:
        validate(instance=file_json, schema=schema)
    except:
        return False
    return True
    

@app.route("/upload_file", methods=["GET","POST"])
def upload_file():
    """Upload a file given by the user to the Saves folder"""
    if request.method=="POST":
        if "file" not in request.files:
            return "ERROR: No file in request", 404
        file=request.files["file"]
        if file.filename=="":
            return "ERROR: No selected file", 400
        print(f"File is: {file}. Filename is: {file.filename}")
        # # if the file exists and it's of the right extension in the right format
        if file and check_allowed_extension(file.filename):
            filename = secure_filename(file.filename)
            upload_folder=app.config.get("UPLOAD_FOLDER")
            #make upload_folder if it doesn't exist
            # if not os.path.isdir(upload_folder):
            #     os.makedirs(upload_folder)

            file_path=os.path.join(upload_folder,filename)
            file.save(file_path)
            return "file saved"
        else:
            return "File exists but wasn't uploaded"


# @app.route("/load_file")
# def load_ll_from_file():
#     """Load new linked list from a save file"""
#     with open('strings.json') as f:
#         d = json.load(f)
#         print(d)
#     #if the linked list already has nodes in it, throw an overwrite warning
#     if ll.returnLL()!="null":


    

## TEST FUNCTIONS
@app.route("/test/add_singular",methods=["GET","POST"])
def test_add_singular():
    q=QTypeOptions("singular")
    a=ATypeOptions("open-ended")
    # print(q,a)
    new_question=Question("example question","single example",q,a)
    print(f"New singular question: {new_question}")
    new_node=Node(new_question)
    print(f"New node: {new_node}")
    ll.append(new_node)
    ll.printLL()
    return "singular works"
@app.route("/test/add_base",methods=["GET","POST"])
def test_add_base():
    q=QTypeOptions("base")
    a=ATypeOptions("open-ended")
    # print(q,a)
    new_question=Question("example question","base example",q,a)
    print(f"New base question: {new_question}")
    new_node=Node(new_question)
    print(f"New node: {new_node}")
    ll.append(new_node)
    ll.printLL()
    return "base works"
@app.route("/test/add_addon",methods=["GET","POST"])
def test_add_addon():
    q=QTypeOptions("add-on")
    a=ATypeOptions("multiple-choice")
    new_question=Question("addon question","ex detail",q,a)
    print(f"New addon question: {new_question}")
    base_detail="base example"
    base_node=ll.getByDetail(base_detail)
    base_node.addon=new_question
    print(f"Addon \"{new_question.q_str}\" added to base node \"{base_node.question.q_detail}\"")
    return "addon works"
@app.route("/test/post_question",methods=["POST"])
def test_post_question():
    result=request.form
    q=QTypeOptions("singular")
    a=ATypeOptions("multiple-choice")
    new_question=Question(result["question"],result["detail"],q,a)
    print("Created question:",new_question)
    new_node=Node(new_question)
    ll.append(new_node)
    ll.printLL()
    return {"response":"added question"}
@app.route("/test/print_all", methods=["GET"])
def print_all():
    ll.printLL()
    return {"result":ll.returnLL()}

import signal
def shutdown_server()->str:
    os.kill(os.getpid(), signal.SIGINT)
    return " Flask server shutdown"
@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        for key in redis_url.keys("session:*"): # Important: Use a pattern to only delete session keys
            redis_url.delete(key)
        res="Redis sessions cleared."
        # print(res)
    except Exception as e:
        res=f"Error clearing Redis sessions: {e}"
        # print(res)
    try:
        res+=shutdown_server()
    except Exception as e:
        res+=" Shutdown error"
    return res

# print(app.url_map)
# import sys
# print("Executing in",sys.executable)
# if "jsonschema" in sys.modules:
#     print("JSONSchema is in the modules")
# else:
#     print("jsonschema isn't in the modules")

if __name__ == "__main__":
    # app.run(debug=True, use_reloader=False)
    app.run(debug=True)