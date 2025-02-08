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

# Singleton metaclass
# NOTE: Need to test in production, may cause errors
class Singleton(type):
    _instance=None
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance=super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance
class DetailList(metaclass=Singleton):
    def __init__(self):
        self.content:list[str]=[]
    def __str__(self):
        return f"{self.content}"
    def add(self,value):
        self.content.append(value)
    def get(self):
        return self.content



# ROUTES
from flask import Flask, request, session
from flask_session import Session
from flask_cors import CORS
#for clearing session files
import os, sys, glob, atexit

app = Flask(__name__)

app.config['SECRET_KEY'] = "YourSecretKey@123"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT']= False
# Initialize Plugins
Session(app)
CORS(app)


# Session(app)
ll=LinkedList() #initialize linked list to be used later

#check that the server's running and connected
@app.route("/", methods=["GET","POST"])
def check():
    print("Working directory path is",os.getcwd(),". Current directory path is",os.path.dirname(os.path.abspath(sys.argv[0])))
    return {"result":"Server active!"}

@app.route("/add_question", methods=["POST"])
def add_question():
    """Make a new Question with the info passed"""
    result=request.form
    print(result)
    # print(type(result["q_type"]))
    # print(ATypeOptions("multiple-choice"))
    # print(ATypeOptions(result["a_type"]))
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

## ERROR!!!: This only works as a Flask app
##  It seems like every time this is run, it makes a new session variable, rather than getting the old one
@app.route("/add_detail/<detail>",methods=["GET","POST"])
def add_detail_to_list(detail):
    """Add a q_detail to a list of q_details"""
    # Initialize the list if it doesn't exist
    if 'lst' not in session:
        print("Session variable not found. Initializing...")
        session['lst'] = []
        session.modified = True

    # Append to the list
    lst:list[str]=session['lst']
    print("Before appending:",lst)
    lst.append(detail)
    print("After appending:",lst)
    session['lst'] = lst
    session.modified = True
    
    return {"response":f"existing details are {lst}"}
@app.route("/get_all_details",methods=["GET"])
def get_all_details():
    details:list[str]=session.get("lst",[])
    return {"result":details}


@app.route("/print_all", methods=["GET"])
def print_all():
    ll.printLL()
    return {"result":ll.returnLL()}

@app.route("/get_all_base_details", methods=["GET"])
def get_all_base_details():
    """Get the details of all nodes with the q_type 'base'"""
    base_list=ll.getByQType("base")
    return {"result":base_list}

@app.route("/get_ll_json", methods=["GET"])
def all_to_json():
    """Get every node in the linked list and return them as json"""
    print(ll.getAll())
    return {"result":ll.getAll()}
    

## TEST FUNCTIONS
@app.route("/test_add_singular",methods=["GET","POST"])
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
@app.route("/test_add_base",methods=["GET","POST"])
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
@app.route("/test_add_addon",methods=["GET","POST"])
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

# # NOTE: Make sure this works in production
# def clear_session(dir,pattern):
#     """Deletes files matching the given pattern."""
#     cache_files = glob.glob(os.path.join(dir,pattern))
#     for file_path in cache_files:
#         try:
#             os.remove(file_path)
#             print(f"Deleted: {file_path}")
#         except FileNotFoundError:
#             print(f"File not found: {file_path}")
#         except Exception as e:
#             print(f"Error deleting {file_path}: {e}")
# current_dirctory=os.path.dirname(os.path.abspath(sys.argv[0]))
# full_path=os.path.join(current_dirctory,"flask_session")
# atexit.register(clear_session,dir=full_path,pattern="*")

# print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)