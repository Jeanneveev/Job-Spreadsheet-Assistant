I decided to restart the project due to problems closing background processes in v2 that I could not figure out how to fix without messing up the Electron app. I read the book Architecture Patterns with Python by Harry Percival and Bob Gregory and quickly realized that I had fallen into a number of pitfalls they mention. Thus, I decided to begin v3 while going along with the book as recommended in its preface.

I began by making the domain model by following Test-Driven Development practices. I begun by writing out a summary of the project's MVP in domain language, resulting in the following description:
"The app should allow the user, the **applier**, to enter job details into a form, which will then be appended as a row to a Google Sheets file. The **prompts** for the form to get the job details come from a series of user created **question sets**.

A **question set** is made up of a set of **questions**. A **question** is defined by its **id**, **text**, **q_type**, **answ_type**, **answ_part**, and **choices**.
The **id** is the unique id for a given question
The **text** is the text of the question, which will appear as the prompt in the form
The **q_type**, short for **question_type** is the type of the question. The q_type can be **multiple-choice**, **open-ended**, or **preset**
The **answ_type** is the type of answer the question receives. This can be a **singular** answer or a **two-part** answer
The **answ_part** only exists if the answ_type is two-part. The parts can be the **base** answer or the **addon** answer
The **choices** only exist if the q_type is multiple-choice and are a preset list of choices the user can select to answer the prompt with

The user answers prompts made from question texts for each question in the set. They can answer the next question or go back to change their answer to the previous question. Once they reach the last question, the user should be asked to confirm their decisions. If so, the answers from the form are turned into a row of a given Google Sheets page and appended to the end of it."

Based off of this revised summary, I began making my first tests. Early on, I thought that the Question class I had initially imagined like:
```
class Question:
    def __init__(self, id:int, text:str, q_type:str, answ_type:str, answ_part:str=None, choices:list[str]=None):
        self.id = id
        self.text = text
        self.q_type = q_type
        self.answ_type = answ_type
        self.answ_part = answ_part
        self.choices = choices
```
was too bloated. Specifically, this thought came about when I was thinking of how to test that addon questions should have a reference to the id of a certain base question. This would require adding some attribute `base_id`, which would mean that 3 of the 7 attributes of the class are not only optional, but based on other attributes of the class. Thus, I tried to change it by implementing subclasses and a factory pattern, but that didn't work due to the many ways question types can be combined. So, in the end, I settled for a dataclass with a lot of post-initialization validation.
