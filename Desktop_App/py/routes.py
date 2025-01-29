from flask import Flask, jsonify
app = Flask(__name__)

list_o_answers:list[str]=[]
list_o_questions:list[str]=[]
list_o_sums:list[int]=[]

@app.route("/", methods=["GET","POST"])
def check():
    return {"result":"Server active!"}

@app.route("/add/<num1>/<num2>", methods=["POST"])
def addNumbers(num1,num2):
    num1=int(num1)
    num2=int(num2)
    sum = num1+num2
    list_o_sums.append(sum)
    return {"sum":f"{num1}+{num2}={sum}"}

@app.route("/appendAnswer/<some_value>", methods=["POST"])
def appendToList(some_value):
    if some_value=="null":
        some_value=""
    list_o_answers.append(some_value)
    print(f"Appended {some_value}")
    return {"value":some_value}

# @app.route("/appendQuestion/<question>", methods=["POST"])
# def appendQuestion(question):
#     list_o_questions.append(question)
#     print(f"Appended {question}")
#     return {"value":question}

@app.route("/getAllAnswers", methods=["GET"])
def getAllAnswers():
    return jsonify(answers=list_o_answers)

print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True)