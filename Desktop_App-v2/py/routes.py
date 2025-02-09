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
from flask import Flask, request, session
from flask_session import Session
from flask_cors import CORS
import redis, json
#for clearing session files
import os, sys, atexit

app = Flask(__name__)

# Configurations
app.config["SECRET_KEY"]="change_later"
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_PERMANENT"] = False
#configure settings so Flask can recognize the frontend session ID cookie
app.config["SESSION_COOKIE_SAMESITE"]="None"
app.config["SESSION_COOKIE_SECURE"]=True
r = redis.from_url('redis://127.0.0.1:6379')
app.config['SESSION_REDIS'] = r
def test_redis_connection(redis_session):
    """Check that Redis is connected to"""
    try:
        redis_session.ping()  # Check if Redis is alive
        print("Redis connection successful!")
    except redis.exceptions.ConnectionError as e:
        print(f"Redis connection error: {e}")
        exit()  # Or handle the error appropriately
test_redis_connection(r)
app.config["CORS_HEADERS"] = "Content-Type"

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
@app.route("/test_post_question",methods=["POST"])
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

## NOTE: Make sure this works in production
def clear_redis_sessions(redis_session):
    """Clears all session data from Redis."""
    try:
        for key in redis_session.keys("session:*"): # Important: Use a pattern to only delete session keys
            redis_session.delete(key)
        print("Redis sessions cleared.")
    except Exception as e:
        print(f"Error clearing Redis sessions: {e}")
atexit.register(clear_redis_sessions,redis_session=r)  # Register the cleanup function


# print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)