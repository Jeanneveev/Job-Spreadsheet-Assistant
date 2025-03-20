from enum import Enum
from typing import Any
from datetime import date
## Google Sheets Stuff
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import sheetsConfig, basedir
## NOTE: If modifying this scope, delete the file token.json.
SPREADSHEET_ID=sheetsConfig.SPREADSHEET_ID

class QTypeOptions(Enum):
    SINGULAR="singular"
    BASE="base"
    ADD_ON="add-on"
class ATypeOptions(Enum):
    MULT="multiple-choice"
    TEXT="open-ended"
    PRESET="preset"
class Question:
    def __init__(self,q_str:str,q_detail:str,q_type:QTypeOptions,a_type:ATypeOptions,choices:list[str]=None)->None:
        self.q_str=q_str
        self.q_detail=q_detail
        self.q_type=q_type
        self.a_type=a_type
        self.choices=choices
    def __str__(self)->str:
        return f"{self.q_detail}"
    def as_dict(self)->dict:
        res_d={"q_str":self.q_str,"q_detail":self.q_detail,
                "q_type":self.q_type.value,"a_type":self.a_type.value}
        if self.choices:
            res_d["choices"]=self.choices
        return res_d
class Node:
    def __init__(self,question):
        self.question:Question=question
        self.addon:Question=None
        self.answer:str=None
        self.next:Node=None
        self.prev:Node=None
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
    def display_info(self,requesting_addon:bool,requesting_last:bool)->dict:
        """Return only the necessary information for displaying this Node's Question in the frontend
        Parameters:
            self: Node - The current instance of a Node
            requesting_addon: bool - Whether or not the question of the Node that's being requested is its addon Question
            requesting_last: bool - Whether or not the question that's being asked for is the last Question in the linked list
        
        Returns:
            A dictionary with the following keys:
                "q_str": str - The q_str of the requested question
                "next_question_a_type": str - The value of the a_type of the next question
                "is_last": str - Whether or not the requested question is the last question
        """
        if not requesting_last:
            if requesting_addon:
                requested_question:Question=self.addon
                next_question:Question=self.next.question
            else:
                requested_question:Question=self.question
                #if the current question is a base question with an addon, the next question is its addon,
                # else its the question of the next Node
                if self.addon is not None:
                    next_question:Question=self.addon
                else:
                    next_question:Question=self.next.question
            return {"q_str":requested_question.q_str,"next_question_a_type":next_question.a_type.value,"is_last":"false"}
        else:
            if requesting_addon:
                requested_question:Question=self.addon
            else:
                requested_question:Question=self.question
            return {"q_str":requested_question.q_str,"is_last":"true"}
        
        
class LinkedList:
    def __init__(self):
        self.head:Node=None
        self.tail:Node=None

    def append(self,node:Node)->None:
        """Append node to end of linked list"""
        if self.head is None:
            self.head=node
            self.tail=node
            return
        #add node to the end of the linked list
        self.tail.next=node
        #set the prev of the Node
        node.prev=self.tail
        #update linked list tail
        self.tail=node

    def printLL(self):
        """Print all of the linked list's node's details"""
        curr=self.head
        while curr:
            print(curr.question,end="->")
            curr=curr.next
        print("null")
    def returnLL(self):
        """Return a string of all the ll's node's details"""
        curr=self.head
        res=""
        while curr:
            res+=f"{curr.question.q_detail}->"
            curr=curr.next
        res+="null"
        return res
    def getByQType(self,val:str)->list[str]:
        """Search linked list for all nodes with a certain q_type"""
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
        """Search linked list by detail"""
        ## NOTE: I feel like I could add some caching to this function
        curr:Node=self.head
        while curr:
            if curr.question.q_detail==val:
                # print("matched")
                return curr
            curr=curr.next
        return None
    def getByIdx(self,idx)->Node:
        """Search linked list by index"""
        curr:Node=self.head
        i=0
        while curr:
            if i==idx:
                return curr
            i+=1
            curr=curr.next
        raise IndexError("Index out of range")
    def getAll(self)->list[dict]:
        """Return a list of the dictionary forms of all the nodes"""
        res=[]
        curr:Node=self.head
        while curr:
            res.append(curr.as_dict())
            curr=curr.next
        return res
    def clear(self):
        """Removes the linked list from memory"""
        # With the head set to None, the old linked list is now no longer referenced,
        # and will be cleared by Python's garbage collection
        self.head=None

class ExportDataError(Exception):
    """ A base class for ExportData-related exceptions """
class AuthenticationError(ExportDataError):
    """Exception raised for errors relating to failed authentication attempts"""
class TokenFetchError(ExportDataError):
    """Exception raised for errors fetching a token"""
class ServiceBuildError(ExportDataError):
    """Exception raised for errors building the Google API service"""

class ExportData:
    """
    A class that holds the info and methods for data exportation

    Attributes
    ----------
    data : list[str]
        a list of all the answers given
    method : str
        the type of what is being exported to ( e.g. CSV, Google Sheets )
    loc : str
        the location of the export ( currently only planned to be used for the pathstring of the export csv )
    """
    def __init__(self):
        self.data:list[str]=None
        self.method:str=None
        self.service=None
        self.loc=None
    # CSV
    def export_to_CSV(self):
        if self.loc==None:
            raise FileNotFoundError
        pass
    # GOOGLE SHEETS
    def get_auth_url(self)->str|None:
        """A function to send the URL of the log-in page for the frontend to open,
            allow for user certification, and send back that certification via another route
        """
        SCOPES=["https://www.googleapis.com/auth/spreadsheets"]
        creds=None
        token_path=os.path.join(basedir,"token.json")
        if os.path.exists(token_path):
            creds=Credentials.from_authorized_user_file(token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:   #creds.refresh_token is also expired
                    print(f"Refresh error: {e}")
                    #delete token.json and re-run function so the if statement fails
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    return self.get_auth_url()
            else:
                #redirect_uri is the page Google redirects to after sign-in is complete
                flow = InstalledAppFlow.from_client_secrets_file(
                    "py/sheets_credentials.json", SCOPES, redirect_uri="http://127.0.0.1:5000/auth_landing_page/"
                )
                #get and return the auth url
                auth_url, _= flow.authorization_url()
                return auth_url
        return None

    def get_service(self,code=None)->Any|dict|HttpError:
        """Connects to the Google Sheets API
        Args:
            code: The authentification code gotten from the user login
        Returns:
            service (Any): the connection to the API
            error (dict): a error message
            error (HttError): an HttpError
        """
        ## NOTE: If modifying this scope, delete token.json file
        SCOPES=["https://www.googleapis.com/auth/spreadsheets"]
        creds=None  #initialize creds
        # If there is already a token.json, just get the credentials from it
        token_path=os.path.join(basedir,"token.json")
        if os.path.exists(token_path):
            creds=Credentials.from_authorized_user_file(token_path, SCOPES)
            print(f"Credentials from token.json: {creds}")
        #if there isn't or the credentials aren't valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError as e:   #creds.refresh_token is also expired
                    print(f"Refresh error: {e}")
                    #delete token.json and re-run function so the if statement fails
                    if os.path.exists(token_path):
                        os.remove(token_path)
                    return self.get_service()
            elif code:
                creds_path=os.path.join(basedir,"sheets_credentials.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, SCOPES, redirect_uri="http://127.0.0.1:5000/auth_landing_page/"
                )
                #try getting the token of the credentials from the auth code
                try:
                    flow.fetch_token(code=code)
                    creds=flow.credentials
                    with open(token_path, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"ERROR!! Error fetching token: {e}")
                    raise TokenFetchError("Error authenticating via code") from e
            else:   #no creds or code
               raise AuthenticationError("No valid credits or code. User could not be authenticated")
            
        #try and return the build
        try:
            if creds is None:
                raise AuthenticationError("Credentials are None")
            if not creds.valid:
                raise AuthenticationError("Credentials are invalid")
            # print(f"Credentials are: {creds}")
            self.service = build("sheets", "v4", credentials=creds)
            # print("service gotten")
            return self.service
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise ServiceBuildError(f"Some error occured with Google Sheets' API: {error}")
        except AuthenticationError as error:
            print(f"An Authentication error occurred: {error}")
            raise ServiceBuildError(f"Authentication error: {error}")
    
    def length_to_col_letter(self,length:int):
        num2char={1:"A",2:"B",3:"C",4:"D",5:"E",
                  6:"F",7:"G",8:"H",9:"I",10:"J",
                  11:"K",12:"L",13:"M",14:"N",15:"O",
                  16:"P",17:"Q",18:"R",19:"S",20:"T",
                  21:"U",22:"V",23:"W",24:"X",25:"Y",26:"Z"}
        col=""
        if length>26:
            len1=length//26
            len2=length%26
            col=num2char[len1]+num2char[len2]
        else:
            col=num2char[length]
        return col
    def export_to_sheets(self)->Any|dict:
        """Appends the list of details as a new row of a Google Sheets spreadsheet
        Args:
            self: The current instance of ExportData
        Returns:
            result (Any): The confirmation that the cells were appended
            dict: A dictionary with the key "error" and the error message
        """
        try:
            if self.service is None:
                # print("Check 1, self.service is None")
                self.get_service()  #ensure self.service is set
            if self.service is None:    #check again
                # print("Check 2: self.service is still None")
                raise ServiceBuildError("Google Sheets service could not be obtained.")
        except AuthenticationError as e:
            print(f"Authentication error: {e}")
            return {"error": f"{e}"}, 400
        except TokenFetchError as e:
            print(f"TokenFetch error: {e}")
            return {"error": f"{e}"}, 404
        except ServiceBuildError as e:
            print(f"ServiceBuild error: {e}")
            return {"error": f"{e}"}, 501
        except Exception as e:
            print(f"An error has occured: {e}")
            return {"error": f"{e}"}, 404
        data=self.data
        end_col=self.length_to_col_letter(len(data))
        rnge=f"A2:{end_col}2"

        try:
            values=[data]
            body={"values": values}
            result=(
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=SPREADSHEET_ID,
                    range=rnge,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            # print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            return {"error": f"{error}"}



# ROUTES
from flask import Flask, request, session, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
app.config.from_object("config.Config")

# Initialize Plugins
CORS(app,supports_credentials=True)


ll=LinkedList() #initialize linked list to be used later
exportData=ExportData() #initialize the method of exporting the data, to be set later

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
    print("Form is", result)
    #all of the form sections are required, so we don't need to check for NULLs
    # however, we do need to check if base or add-on was selected because they're in their own group
    if "q_type_2" in result:
        q_type=QTypeOptions(result["q_type_2"])
    else:
        q_type=QTypeOptions(result["q_type"])
    a_type=ATypeOptions(result["a_type"])
    #if it's a multiple-choice question, get the choices
    if a_type.value=="multiple-choice":
        print("Creating new multiple-choice question")
        choices:list[str]=json.loads(result["choices"])
        print("Choices are:",choices)
        new_question=Question(result["question"],result["detail"],q_type,a_type,choices)
    else:
        new_question=Question(result["question"],result["detail"],q_type,a_type)
    print("Created question:",new_question)
    new_node=Node(new_question)
    ll.append(new_node)
    ll.printLL()
    if a_type.value=="multiple-choice":
        return {"mult_response": "added question"}
    else:
        return {"response":"added question"}
@app.route("/add_question/addon", methods=["POST"])
def add_addon():
    result=request.form
    #make a question from the results
    q_type=QTypeOptions(result["q_type_2"])
    a_type=ATypeOptions(result["a_type"])
    if a_type.value=="multiple-choice":
        print("Creating new multiple-choice question")
        choices:list[str]=json.loads(result["choices"])
        print("Choices are:",choices)
        new_question=Question(result["question"],result["detail"],q_type,a_type,choices)
    else:
        new_question=Question(result["question"],result["detail"],q_type,a_type)
    #get the node of the question this one is adding onto
    base_detail=result["addon_to"]
    base_node=ll.getByDetail(base_detail)
    #set the base's addon value to the addon Question
    base_node.addon=new_question
    print(f"Addon \"{new_question.q_detail}\" added to base node \"{base_node.question.q_detail}\"")
    if a_type.value=="multiple-choice":
        return {"mult_response": "added multiple-choice addon question"}
    else:
        return {"response":"added addon question"}
## ADD PRESET QUESTIONS
def add_application_date():
    # create a Question with an a_type of "preset" where the value is the current date
    new_q=Question("appDate","Application Date",QTypeOptions("singular"),ATypeOptions("preset"))
    new_node=Node(new_q)
    ll.append(new_node)
    print("New preset node appended")
def add_empty_question(i):
    #create a preset Question with an empty value for empty columns
    new_q=Question("empty",f"Empty-{i}",QTypeOptions("singular"),ATypeOptions("preset"))
    new_node=Node(new_q)
    ll.append(new_node)
    print("New preset node appended")
@app.route("/add_question/preset", methods=["POST"])
def add_preset():
    value:str=request.get_json()["preset"]
    match value:
        case "appDate":
            add_application_date()
        case "empty":
            empty_cntr=session.get("empty_cntr",0)
            add_empty_question(empty_cntr)
            session["empty_cntr"]=empty_cntr+1
    return f"{value} Question added"

## DETAILS
@app.route("/add_detail/<detail>",methods=["GET","POST"])
def add_detail_to_list(detail):
    """Add a q_detail to a list of q_details"""
    # Initialize the list if it doesn't exist
    if 'detail_lst' not in session:
        print("Session variable not found. Initializing...")
        session['detail_lst'] = json.dumps([])
        session.modified = True
    # Append to the list
    detail_lst:list[str]=json.loads(session['detail_lst'])
    print("Before appending:",detail_lst)
    detail_lst.append(detail)
    print("After appending:",detail_lst)
    session['detail_lst'] = json.dumps(detail_lst)
    session.modified = True

    return {"response":f"{detail_lst}"}
@app.route("/get_all_details",methods=["GET"])
def get_all_details():
    details:list[str]=session.get("detail_lst",[])
    return {"result":details}
@app.route("/check_detail/<detail>")
def check_detail(detail):
    details:list[str]=session.get("detail_lst",[])
    if detail in details:
        return {"result":"True","detail_list":details}
    else:
        return {"result":"False","detail_list":details}


@app.route("/get_all_base_details", methods=["GET"])
def get_all_base_details():
    """Get the details of all nodes with the q_type 'base'"""
    base_list=ll.getByQType("base")
    return {"result":base_list}

## CHOICES
@app.route("/set_curr_choices", methods=["POST"])
def set_curr_choices():
    """Set the past list of options as the value of curr_opt_lst"""
    options=request.get_json()["choices"]
    # Remove duplicates NOTE: Can't use set because it's unordered
    options=list(dict.fromkeys(options))
    session['curr_opt_lst']=options
    session.modified = True
    return "Current options set",200

@app.route("/add_choices", methods=["POST"])
def add_choices_to_list():
    """Add any number of passed options to the overall list of options"""
    options=request.get_json()["choices"]
    # print("Options are", options)
    # Initialize the lists if they don't exist
    if 'all_opt_lst' not in session:
        # print("Session variable not found. Initializing...")
        session['all_opt_lst'] = []
        session.modified = True
    # Append to the list
    all_opt_lst:list[str]=session['all_opt_lst']
    # print("Before appending:",all_opt_lst,curr_opt_lst)
    all_opt_lst.extend(options)
    # print("Before setting:",all_opt_lst,curr_opt_lst)
    # Remove duplicates NOTE: Can't use set because it's unordered
    all_opts=list(dict.fromkeys(all_opt_lst))
    # print("After setting:",all_opts,curr_opts)
    # Turn back into lists in order to be serializable
    all_opt_lst=list(all_opts)
    # print("After appending:",all_opt_lst,curr_opt_lst)
    session['all_opt_lst'] = all_opt_lst
    session.modified = True
    return "Options added to all list"

@app.route("/get_all_choices",methods=["GET"])
def get_all_choices():
    options:list[str]=session.get("all_opt_lst",[])
    return jsonify({"result":options})
@app.route("/get_current_choices",methods=["GET"])
def get_curr_options():
    options:list[str]=session.get("curr_opt_lst",[])
    return jsonify({"result":options})

@app.route("/clear_current_choices",methods=["GET"])
def clear_current_choices():
    """Clear the curr_options session variable"""
    if 'curr_opt_lst' in session:
        print("Now clearing curr_opt_lst")
        session['curr_opt_lst'] = []
        session.modified = True
    options:list[str]=session.get("curr_opt_lst")
    return f"Current options cleared. curr_opt_lst is now {options}"
## VIEW
@app.route("/get_ll_json", methods=["GET"])
def all_to_json():
    """Get every node in the linked list and return them as json"""
    # print("Linked list JSON is: ",ll.getAll())
    return {"result":ll.getAll()}
## ORDER
@app.route("/reorder_questions", methods=["POST"])
def reorder_nodes():
    """Upon being given an ordered list of node details, reorder the linked list to be in that order"""
    global ll
    ordered_dict:dict=request.get_json()["order"]
    print(f"The ordered dict is {ordered_dict}. It is of type {type(ordered_dict)}")
    new_ll=LinkedList()

    for k,v in ordered_dict.items():
        node:Node=ll.getByDetail(v)
        #NOTE: Clearing the node's pointers here is key, or else it will cause an infinite loop
        node.next=None
        node.prev=None
        new_ll.append(node)
    ll=new_ll
    ll.printLL()

    return ""
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
    """Given JSON of a file, confirm that it's in the right format to be turned into a LinkedList object"""
    schema={
        "type":"array",
        "items": {
            "type":"object",
            "properties": {
                "question": {
                    "type":"object",
                    "properties": {
                        "q_str": {"type":"string"},
                        "q_detail": {"type":"string"},
                        "q_type": {"type":"string"},
                        "a_type": {"type":"string"},
                        "choices": {"type":"array"}
                    },
                    "required":["q_str","q_detail","q_type","a_type"]
                },
                "addon": {
                    "type":"object",
                    "properties": {
                        "q_str": {"type":"string"},
                        "q_detail": {"type":"string"},
                        "q_type": {"type":"string"},
                        "a_type": {"type":"string"},
                        "choices": {"type":"array"}
                    },
                    "required":["q_str","q_detail","q_type","a_type"]
                },
                "answer": {
                    "type":"string"
                },
            },
            "required":["question"]
        }
    }
    try:
        validate(instance=file_json, schema=schema)
    except:
        return False
    print("file validated")
    return True

@app.route("/upload_file", methods=["GET","POST"])
def upload_file():
    """Upload a file given by the user to the Saves folder"""
    if request.method=="POST":
        if "file" not in request.files:
            return "ERROR: No file in request", 404
        file=request.files["file"]
        if file.filename=="":
            return "ERROR: No selected file", 404
        
        file_json=json.load(file)   #this puts the file stream pointer at the end
        file.seek(0)    #reset file pointer to the start
        print(f"File is: {file_json}. Filename is: {file.filename}")
        # if the file exists and it's of the right extension in the right format
        if file and check_allowed_extension(file.filename):
            if validate_upload(file_json):
                file.seek(0)    #reset file pointer to the start (validate should have put it at the end again)
                filename = secure_filename(file.filename)
                upload_folder=app.config.get("UPLOAD_FOLDER")

                file_path=os.path.join(upload_folder,filename)
                file.save(file_path)    #save as a local file
                load_ll_from_file(file_json)    #save in the linked list
                return "File saved", 201
            else:
                return "Wrong file format", 400
        else:
            return "File exists but wasn't uploaded", 409

def load_ll_from_file(file_json):
    """Load new linked list from a saved file's JSON"""
    # clear old linked list
    ll.clear()
    # parse JSON into new linked list
    for node in file_json:
        question=node["question"]
        q_type=QTypeOptions(question["q_type"])
        a_type=ATypeOptions(question["a_type"])
        new_question=None
        if "choices" in question:
            new_question=Question(question["q_str"],question["q_detail"],q_type,a_type,question["choices"])
        else:
            new_question=Question(question["q_str"],question["q_detail"],q_type,a_type)
        new_node=Node(new_question)
        #if there's an addon, make a Question out of it and add it to the new node
        if "addon" in node:
            addon=node["addon"]
            addon_q_type=QTypeOptions(addon["q_type"])
            addon_a_type=ATypeOptions(addon["a_type"])
            new_addon=None
            if "choices" in addon:
                new_addon=Question(addon["q_str"],addon["q_detail"],addon_q_type,addon_a_type,addon["choices"])
            else:
                new_addon=Question(addon["q_str"],addon["q_detail"],addon_q_type,addon_a_type)
            new_node.addon=new_addon
        ll.append(new_node)
    

## ANSWER
def get_first_non_preset_node()->Node|None:
    """Returns the first Node whose question's a_type is not preset, if any"""
    head:Node=ll.head
    result_node:Node=head
    a_type_val=head.question.a_type.value
    if a_type_val!="preset":
        return result_node
    
    while a_type_val=="preset" and head is not None:
        a_type_val=head.question.a_type.value
        result_node=head
        head=head.next
    if a_type_val=="preset":    #all questions are preset questions
        return None
    return result_node
def get_next_non_preset_question(forwards:bool)->Node|None:
    """Return the first question before or after the current question whose a_type is not preset, if any"""
    #NOTE: It should be impossible for one to go back into a series of preset questions that start the ll
    # because the button would be disabled on the frontend, however, it is possible to go forwards into a series of presets that end it
    
def answer_starter_presets():
    """Loop backwards from the first non-preset node and answer all, if any, preset nodes before it"""
    curr:Node=get_first_non_preset_node()
    if curr!=ll.head:
        while curr!=ll.head: 
            curr=curr.prev
            #Find what preset question the node contains and answer it
            which_preset:str=curr.question.q_str
            answ=""
            match which_preset:
                case "appDate":
                    answ=answer_application_date()
                case "empty":
                    answ=answer_empty()
            curr.answer=answ

def get_last_question()->Question:
    """Return the last Question in the linked list"""
    if ll.tail.addon is not None:
        return ll.tail.addon
    else:
        return ll.tail.question

@app.route("/get_first_a_type")
def get_first_a_type():
    head:Node|None=get_first_non_preset_node()
    if head is None:    #all questions are preset questions
        return "Please add at least one non-preset question", 202
    else:
        a_type_val=head.question.a_type.value
        return a_type_val
    
@app.route("/get_first_question")
def get_first_question_display_info()->dict:
    """Get the display info of the first non-preset Question in the LinkedList
    
    Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the requested question
            "next_question_a_type": str - The value of the a_type of the next question
            "is_last": str - Whether or not the requested question is the last question
    """
    first_valid:Node=get_first_non_preset_node()
    last_q:Question=get_last_question()
    answer_starter_presets()
    # Set session variables
    session["curr_node"]=first_valid.as_dict()
    session["curr_question"]=first_valid.question.as_dict()

    if first_valid.question==last_q:
        fv_display_info:dict=first_valid.display_info(False,True)
    else:
        fv_display_info:dict=first_valid.display_info(False,False)
    return fv_display_info

@app.route("/get_next_question")
def get_next_question_display_info()->dict:
    """Get the display info of the next question

    Returns:
        res: dict - A dictionary with the following keys:
            "q_str": str - The q_str of the next question
            "next_question_a_type": str - The value of the a_type of the question after the next question
            "is_last": str - Whether or not the next question is the last question
            "is_addon": str - Whether or not the next question is an addon question
    """
    #Get the current node and question
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    curr_question_dict:dict=session["curr_question"]
    on_addon=False
    next_is_addon=False
    if not curr_question_dict==curr_node.question.as_dict():    #the current question is the node's addon question
        on_addon=True

    #Get the next question
    if (on_addon==True) or (curr_node.addon is None):   #the current question is an addon or doesn't have an addon
        #the next question is the next node's question
        next_question:Question=curr_node.next.question
        next_node:Node=curr_node.next
    else:   #the current question has an addon, which will be the next question
        next_question:Question=curr_node.addon
        next_node:Node=curr_node
        next_is_addon=True
    session["curr_question"]=next_question.as_dict()
    session["curr_node"]=next_node.as_dict()

    last_q:Question=get_last_question()
    if next_question==last_q:
        res=next_node.display_info(next_is_addon,True)
    else:
        res=next_node.display_info(next_is_addon,False)
    #append "is_addon" to the dictionary if the next question is one
    if next_is_addon:
        res["is_addon"]="true"
    return res
    
@app.route("/get_prev_question")
def get_prev_question():
    """Get the display info of the previous question
    
     Returns:
        A dictionary with the following keys:
            "q_str": str - The q_str of the previous question
            "next_question_a_type": str - The value of the a_type of the current question
            "is_last": str - Whether or not the previous question is the last question (should always be false)
            "is_first": str - Wheter or not the previous question is the first question
            "is_addon": str - Whether or not the next question is an addon question
    """
    #Get the current node and question
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the current node by the detail
    curr_question_dict:dict=session["curr_question"]
    on_addon=False
    prev_is_addon=False
    if not curr_question_dict==curr_node.question.as_dict():    #the current question is the node's addon question
        on_addon=True

    #Get the previous question
    if on_addon:    #the current question is an addon and the previous question is its base
        prev_node:Node=curr_node
        prev_question:Question=curr_node.question
    else:   #the previous question is in the previous node
        prev_node:Node=curr_node.prev
        if prev_node.addon is not None:
            prev_question:Question=prev_node.addon
            prev_is_addon=True
        else:
            prev_question:Question=prev_node.question
    session["curr_question"]=prev_question.as_dict()
    session["curr_node"]=prev_node.as_dict()
    
    res=prev_node.display_info(prev_is_addon,False)
    first_q:Question=ll.head.question
    if prev_question==first_q:
        res["is_first"]="true"
    if prev_is_addon:
        res["is_addon"]="true"
    return res

    
@app.route("/get_answer_options", methods=["GET"])
def get_answer_options():
    if "curr_node" in session:
        curr_node_dict:dict=session["curr_node"]
        curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])   #get the node from the detail
    else:
        curr_node:Node=ll.head
    if "curr_question" in session:
        curr_question_dict:dict=session["curr_question"]
        if curr_question_dict==curr_node.question.as_dict():
            curr_question:Question=curr_node.question
        else:
            curr_question:Question=curr_node.addon
    else:
        curr_question:Question=ll.head.question
    return jsonify({"options":curr_question.choices})


@app.route("/add_answer/<answ>",methods=["POST"])
def add_answer(answ):
    curr_node_dict:dict=session["curr_node"]
    #get the node from the detail
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    curr_node.answer=answ
    print(f"Answer {answ} set")
    return f"Answer {answ} set"
@app.route("/add_addon_answer/<answ>",methods=["POST"])
def add_addon_answer(answ:str):
    answer=f" ({answ.lower()})"
    curr_node_dict:dict=session["curr_node"]
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    curr_node_answ=curr_node.answer
    print(f"curr_node_anw is {curr_node_answ}")
    curr_node_answ+=answer
    curr_node.answer=curr_node_answ
    print(f"Answer appended to. Answer is now {curr_node_answ}")
    return f"Answer appended to. Answer is now {curr_node_answ}"

def answer_application_date():
    return date.today().strftime("%m/%d/%Y")
def answer_empty():
    return " "
@app.route("/add_preset_answer",methods=["POST"])
def add_preset_answer():
    curr_node_dict:dict=session["curr_node"]
    #get the node from the detail
    curr_node:Node=ll.getByDetail(curr_node_dict["question"]["q_detail"])
    which_preset:str=request.get_json()["preset"]
    answ=""
    code=200
    match which_preset:
        case "appDate":
            answ=answer_application_date()
        case "empty":
            answ=answer_empty()
            code=201
    curr_node.answer=answ
    return f"Preset answer {answ} set", code



def get_all_answers_handler(by_route:bool):
    """
    A handler function for get_all_answers

    Description: This function gets and returns all of the answers set in
    the linked list and returns it as a list.
    Depending on the value of the by_route parameter, it will return a
    jsonified response or a regular list, to be used by routes and Python
    functions respectively.
    """
    all_nodes_dict=ll.getAll()
    res=[]
    for node_dict in all_nodes_dict:
        if "answer" in node_dict:
            res.append(node_dict["answer"])
    
    if by_route==True:
        return jsonify(res)
    else:
        return res

@app.route("/get_all_answers",methods=["GET"])
def get_all_answers():
    """A route to get the jsonified list of all the answers
        NOTE: Only used for printing to console currently
    """
    return get_all_answers_handler(by_route=True)

## EXPORT
@app.route("/set_export_method/<method>",methods=["POST"])
def set_export_method(method):
    exportData.method=method
    return f"Method {exportData.method} set"
@app.route("/set_export_loc",methods=["POST"])
def set_export_loc():
    upload_folder=app.config.get("UPLOAD_FOLDER")
    file_path=os.path.join(upload_folder,"CSV")
    ### TODO: Replace with the passed filename later
    full_file_path=os.path.join(file_path,"example.csv")
    exportData.loc=full_file_path
    return f"Filepath set as {full_file_path}"
@app.route("/get_export_method",methods=["GET"])
def get_export_method():
    return f"{exportData.method}"
@app.route("/add_all_answers",methods=["POST"])
def add_all_answers():
    answs=get_all_answers_handler(by_route=False)
    exportData.data=answs
    return f"Answers {exportData.data} added"

@app.route("/get_auth_url",methods=["GET"])
def get_auth_url():
    url=exportData.get_auth_url()
    if url:
        print("auth_url is ",url)
        return {"auth_url":url}
    else:
        print("Credentials are already validated")
        return {"message": "Credentials are already validated"}, 200

@app.route("/auth_landing_page/",methods=["GET"])
def auth_landing_page():
    """The page the Google Sheets authorization process lands on after
        a successful login. Includes the auth_code in its parameters
    """
    return "You reached the landing page! You can close this window now."

@app.route("/receive_auth_code",methods=["POST"])
def receive_auth_code():
    code=request.get_json()["code"]
    service=exportData.get_service(code)
    print(f"service is: {service}")
    if type(service)==dict: #it's an error
        return service  #return that error message
    else:
        return {"success_message":"Authentification successful and connection built"}

@app.route("/export_data/sheets",methods=["POST"])
def export_data_sheets():
    export_result=exportData.export_to_sheets()
    print("export_result is",export_result)
    if type(export_result) is tuple:
        error_code=export_result[1]
        export_result=export_result[0]
    if export_result.get("error",None) is None:
        res_msg:str=f"{(export_result.get('updates').get('updatedCells'))} cells appended."
        return res_msg
    else:
        return f"ERROR!!! {export_result.get('error')}",error_code




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
    res=""
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
    print("Flask server running") # Flask ready flag for main.js
    app.run(debug=True, use_reloader=False)
    # app.run(debug=True)