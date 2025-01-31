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
class Node:
    def __init__(self,question):
        self.question:Question=question
        self.answer:str=None
        self.next:Node=None
    def __str__(self)->str:
        return f"The Node is for the question \"{self.question.q_str}\""

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
    def getByQType(self,val:str):
        found:list[str]=[]
        curr:Node=self.head
        while curr:
            print("loop started")
            if curr.question.q_type==QTypeOptions(val):
                print("matched")
                found.append(curr.question.q_detail)
            curr=curr.next
        return found

# ROUTES
from flask import Flask, request
app = Flask(__name__)
ll=LinkedList() #initialize linked list to be used later

#check that the server's running and connected
@app.route("/", methods=["GET","POST"])
def check():
    return {"result":"Server active!"}

##ERROR!!! The updated linked list doesn't seem to save outside of the function, and thus can't be accessed by other functions
#TODO: Think I fixed the error, make sure to check tomorrow
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
    return "works"

@app.route("/test_add_question",methods=["GET","POST"])
def test_add_question():
    q=QTypeOptions("base")
    a=ATypeOptions("open-ended")
    print(q,a)
    new_question=Question("example question","example",q,a)
    print(new_question)
    new_node=Node(new_question)
    print(new_node)
    ll.append(new_node)
    ll.printLL()
    return "works"

@app.route("/get_all", methods=["GET"])
def get_all():
    ll.printLL()
    return {"result":ll.returnLL()}

@app.route("/get_all_base", methods=["GET"])
def get_all_base():
    """Get the details of all nodes with the q_type 'base'"""
    base_list=ll.getByQType("base")
    return {"result":base_list}
    

print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)