from datetime import date
import os
import sys
## Class Imports
#add the parent directory, "py" to sys.path to allow for imports from py/
basedir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# print(f"basedir is {basedir}")
sys.path.append(basedir)
from classes import Question, QTypeOptions, ATypeOptions, Node, LinkedList, ExportData
## Routes Imports
from flask import Flask, request, session, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
app.config.from_object("config.config.Config")

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
###ERROR!!! There's an error where node is None
#   Have set up print statement. TODO: Complete tomorrow
@app.route("/reorder_questions", methods=["POST"])
def reorder_nodes():
    """Upon being given an ordered list of node details, reorder the linked list to be in that order"""
    global ll
    ordered_dict:dict=request.get_json()["order"]
    print(f"The ordered dict is {ordered_dict}. It is of type {type(ordered_dict)}")
    print(f"Before reordering, the ll looks like: {ll.returnLL()}")
    new_ll=LinkedList()

    reordered_nodes:list[Node]=[]
    for k,v in ordered_dict.items():
        print("Reordering",v)
        node:Node=ll.getByDetail(v)
        if node is None:
            return "ERROR: Node not found", 404
        reordered_nodes.append(node)
    #append the reordered nodes
    for node in reordered_nodes:
        #NOTE: Clearing the node's pointers here is key, or else it will cause an infinite loop
        node.next=None
        node.prev=None
        new_ll.append(node)
    ll=new_ll
    print(f"After reordering, the ll looks like: {ll.returnLL()}")

    return "Linked List reordered",200
## DELETE
@app.route("/delete_question", methods=["POST"])
def del_node():
    """Given a node's detail, find and delete it"""
    data=request.get_json()
    if "is_addon" in data:
        is_addon=True
    else:
        is_addon=False
    del_detail:str=request.get_json()["q_detail"]
    print(f"del_detail is {del_detail}")
    if is_addon:
        del_node:Node=ll.getByAddonDetail(del_detail)
    else:
        del_node:Node=ll.getByDetail(del_detail)
    #if the question being deleted is an addon, just delete the addon
    if(del_node.addon):
        if (del_node.addon.q_detail==del_detail):
            del_node.addon=None
            return f"Addon question {del_detail} deleted"
    else:   #otherwise, delete the whole node
        ll.remove(del_node)
        ll.printLL()
        return f"Node {del_detail} deleted"
    
## SAVE
import re
def get_preexisting_filenames():
    """Get all pre-existing question group filenames from the saves
    folder, and database and returns it as a singular list
    """
    print("reached get_preexisting")
    #get from saves folder
    files_filenames:list[str]=[]
    curr_dir=os.path.dirname(__file__)
    path=f"Saves/"
    save_folder=os.path.join(curr_dir, os.pardir, os.pardir, path)
    # print(f"save folder is {save_folder}")
    files=os.listdir(save_folder)
    print(f"files are {files}")
    for file in files:
        print(f"file is {file}")
        if re.match(r"^qg_.*\.json$", file):
            print("matched")
            file_name=file.removeprefix("qg_").removesuffix(".json")
            files_filenames.append(file_name)
        else:
            print("didn't match")
    print(f"files_filenames is {files_filenames}")
    #TODO: Get from database
    db_filenames:list[str]=[]
    #make a combined list with no duplicates
    all_filenames:list[str]=list(set(files_filenames + db_filenames))
    return all_filenames
    
def validate_filename(filename:str):
    """Check that the given filename does not exist within the list
    of existing filenames, and append it to that list if so

    Parameters:
        filename: str - the filename to be checked
    Returns:
        True - A flag representing that filename was not in the list
        and was then appended to it

        False - A flag representing that the filename was in the list
        and was thus not appended to it
    """
    print("validate_filename reached")
    #get the existing filenames from the session variable or from the get_preexisting function
    # if this is the first time this validate function is run
    existing_filenames:list[str]=session.get("filenames",get_preexisting_filenames())
    print(f"existing filenames are {existing_filenames}")
    if filename not in existing_filenames:
        existing_filenames.append(filename)
        session["filenames"]=existing_filenames
        session.modified = True
        return True
    else:
        return False
    
def save_to_database():
    pass

@app.route("/save_file", methods=["POST"])
def write_ll_to_file():
    """Write all nodes of the linked list to a .json file"""
    name:str=request.get_json()["name"]
    print(f"passed name is {name}")
    #convert the given name into a valid filename
    filename=secure_filename(name)
    print(f"secured filename is {filename}")
    if validate_filename(filename): #if the filename is unique
        print(f"filename validated")
        ll_jsonable:list[dict]=ll.getAll()
        curr_dir=os.path.dirname(__file__)
        path=f"Saves/qg_{name}.json"
        save_path=os.path.join(curr_dir, os.pardir, os.pardir, path)

        with open(save_path,"w+", encoding="utf-8") as file:
            json.dump(ll_jsonable,file,ensure_ascii=False,indent=4)

        return f"Question group saved to {save_path}", 200
    else:
        return f"Name already exists", 400
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
        # print(f"File is: {file_json}. Filename is: {file.filename}")
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