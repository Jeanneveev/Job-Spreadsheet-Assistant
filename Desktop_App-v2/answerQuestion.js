/**
 * The parent JS file for shared functions among the answerQuestions pages
 */

const SERVER_URL = "http://127.0.0.1:5000";
const questionHeader=document.getElementById("question");
const form=document.getElementById("form");
const nextBtn=document.getElementById("next");
const prevBtn=document.getElementById("previous");

/* GET QUESTION */
/**
 * For the first question, get the question's text and the info on the next question from the request response
 * For subsequent questions, that info will have been passed into session variables from the question prior,
 * so just get them from there.
*/
let first_q=sessionStorage.getItem("first_q");
let has_next="";
let next_a_type="";

function loadQuestion(){
    if(first_q=="true"){
        console.log("This is the first question");
        /* Set question header */
        fetch(`${SERVER_URL}/get_first_question`,{ method: "GET" })
        .then(response=>response.json())
        .then(data=>{
            questionHeader.innerText=data.q_str;
            has_next=data.has_next;
            console.log("has_next is:",has_next);
            if(has_next=="true"){
                next_a_type=data.next_a_type;
                console.log("next_a_type is",next_a_type)
            }
        })
        .catch(error=>console.error("An error was recieved: ",error));
        prevBtn.disabled=true;  //disable prevBtn
        sessionStorage.setItem("first_q","false");  //change flag
    }else{
        /* Get all the session variables from sessionStorage */
        q=sessionStorage.getItem("next_q_str");
        console.log("q is",q);
        questionHeader.innerText=q;
        has_next=sessionStorage.getItem("has_next");
        if(has_next=="true"){
            next_a_type=sessionStorage.getItem("next_a_type");
            console.log("next_a_type is",next_a_type)
        }else{
            console.log("This is the last question");
        }
        prevBtn.disabled=false; //enable prevBtn
    }
}

/* FORM SUBMISSION */
function submitAnswer(answer){
    answer=answer.trim();
    fetch(`${SERVER_URL}/add_answer/${answer}`,{method:"POST"})
    .then(response=>response.text())
    .then(data=>console.log("data"));
}

/* PREVIOUS QUESTION */
function loadPreviousQuestion(){
    fetch(`${SERVER_URL}/get_prev_question`,{ method: "GET" })
    .then(response=>response.json())
    .then((data)=>{
        if(data.is_first){ //the previous question is the first question
            sessionStorage.setItem("first_q", "true");  //reset flag
        }else{
            /* Set session variables */
            sessionStorage.setItem("next_q_str",data.q_str);
            sessionStorage.setItem("has_next","true");
        }
        //change what page we go to depending on the a_type of the previous question
        if(data.prev_a_type=="multiple-choice"){
            console.log("The previous question is multiple choice");
            form.action="answerQuestion-multiple_choice.html";
        }else if(data.prev_a_type=="open-ended"){
            console.log("The previous question is open-ended");
            form.action="answerQuestion-open_ended.html";
        }
        window.location.href=form.action;   //load page of next question
    });
}

/* NEXT QUESTION */
function loadNextQuestion(){
    //set the text of the next question
    fetch(`${SERVER_URL}/get_next_question`,{ method: "GET" })
    .then(response=>response.json())
    .then((data)=>{
        /* Set all the session variables */
        sessionStorage.setItem("next_q_str",data.q_str);
        console.log("The next question is",sessionStorage.getItem("next_q_str"));
        sessionStorage.setItem("has_next",data.has_next);
        sessionStorage.setItem("next_a_type",data.next_a_type);
        //change what page we go to depending on the a_type of the next question
        if(next_a_type=="multiple-choice"){
            console.log("The next question is multiple choice");
            form.action="answerQuestion-multiple_choice.html";
        }else if(next_a_type=="open-ended"){
            console.log("The next question is open-ended");
            form.action="answerQuestion-open_ended.html";
        }
        window.location.href=form.action;   //load page of next question
    });
}

function addFormListener(openEndedFlag){
    form.addEventListener("submit",(event)=>{
        event.preventDefault();
        submitterId=event.submitter.id;
        if(submitterId=="next"){
            /* Pass the answer to the backend, the value depending on the a_type */
            if(openEndedFlag){
                submitAnswer(input.value);
            }else{
                submitAnswer(document.querySelector('input[name="option"]:checked').labels[0].textContent);
            }
            if(has_next=="true"){   //if there is a next question
                loadNextQuestion();
            }else{                  //this is the last question
                if(confirm("This is the last question. Do you wish to submit all your answers?")){
                    submitLastQuestion();
                }
            }
        }else if(submitterId=="previous"){
            loadPreviousQuestion();
        }
    });
}

/* EXPORTING ANSWERS */
function submitLastQuestion(){
    console.log("Answer submission confirmed");
    /* Add all the answers to be exported */
    fetch(`${SERVER_URL}/add_all_answers`,{ method:"POST" })
    .then(response=>response.text())
    .then(data=>console.log(data));

    /* Send request to connect to export method and upload data */
    fetch(`${SERVER_URL}/get_export_method`,{method: "GET"})
    .then(response=>response.text()).then(data=>{
        console.log("Export method is: ",data);
        if(data=="sheets"){
            return fetch(`${SERVER_URL}/get_auth_url`,{method: "GET"});
        }
    })  //end of get_export_method chain, start of get_auth_url chain
    .then(response=>response.json()).then(data=>{
        /* Sheets */
        if(data.auth_url){
            //send message to ipcMain to open popup and get code
            window.electron.send("open-auth-window", data.auth_url);
        }else if(data.message){ //a valid token.json exists, so there's no need to reauthenticate, just export
            console.log(data.message);
            fetch(`${SERVER_URL}/export_data/sheets`,{ method: "POST" })
            .then(response=>response.text()).then(data=>window.electron.send("open-alert",data));
        }
        /* CSV */
    })
    .catch(err=>console.error("Export request failed",err));
}

/* Listen for the trigger from ipcMain in main.js
 * Activated on the authorization code successfully being gotten
 * Once it is, just pass it to the backend
 */
window.electron.on("auth-code-recieved", (event, code)=>{
    console.log("renderer trigger recieved");
    fetch(`${SERVER_URL}/receive_auth_code`,{
        method: "POST",
        headers:{
            "Content-Type": "application/json",
        },
        body: JSON.stringify({code:code}),
    })
    .then(response=>{
        console.log("Authentification complete");
        return response.json();
    }).then(data=>{
        if(data.success_message){
            console.log(data.success_message);
            /* TODO: Add fetch request to finally export the data */
            fetch(`${SERVER_URL}/export_data/sheets`,{ method: "POST" })
            .then(response=>response.text()).then(data=>alert(data));
        }else{
            //there was an error
            console.error(data.error);
        }
    })
    .catch(err=>console.error("Authentification failed: ",err));
})