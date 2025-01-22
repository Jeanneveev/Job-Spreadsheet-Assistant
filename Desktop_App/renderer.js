import { getQuestionNum,setQuestionNum,pushToBackendList } from "./parent.js"

const question=document.getElementById("question");
const detail=document.getElementById("detail");
const answerForm=document.getElementById("form");
console.log(answerForm)
const input=document.getElementById("user_input");
const submitBtn=document.getElementById("submit");
const resetBtn=document.getElementById("reset");
let numCurrDetail=0;
const details=["JOB NAME","EMPLOYER'S NAME","JOB TYPE (e.g.: contract, full-time, part-time)",
    "JOB LOCATION", "ON-SITE, REMOTE, or HYBRID job","NAME OF THE SITE THE JOB WAS FOUND ON", "LINK TO WHERE THE JOB WAS FOUND",
    "SALARY","YEARLY, MONTHLY, DAILY, or HOURLY payment structure"
]
const detailTypeMap={0:"regular",1:"regular",2:"regular",
    3:"base",4:"addon",5:"regular",6:"regular",
    7:"base",8:"addon"
}    //a map of the indices of details to whether it's a regular or add-odd question
const extraQuestionOptions={4:["On-site","Remote","Hybrid","N/A"],8:["Yearly","Monthly","Hourly","Daily","N/A"]} //map of the indices of extra questions to their list of options
/* TODO: ADD ANOTHER DICT TO ALLOW CUSTOMIZATION OF ADD-ON VALUES IN THE BACKEND INSTEAD OF JUST base (addon) */
detail.innerText=details[numCurrDetail];


input.addEventListener('input', e => {
    submitBtn.innerHTML="Submit";
});

/* FLASK STUFF */
const SERVER_URL = "http://127.0.0.1:5000";
/* test connection - WORKS */
function testConnection(){
    fetch(`${SERVER_URL}/`,{
        method: "GET",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
    }).then(response=>response.json()).then((data)=>{
        //put the result inside the result p
        document.getElementById("test").innerText = data.result;     //data.result should have the result from python script
    })
}
testConnection();

function testPost(num1){
    let num2="10";
    fetch(`${SERVER_URL}/add/${num1}/${num2}`,{
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
    }).then(response=>response.json()).then((data)=>{
        console.log(data.sum);
        document.getElementById("result").innerText = data.sum;
    })
}
// testPost(5);


function setDetailType(){
    switch (detailTypeMap[numCurrDetail]) {
        case "regular":
            sessionStorage.setItem("detailType","regular");
            break;
        case "base":
            sessionStorage.setItem("detailType","base");
            break;
        case "addon":
            sessionStorage.setItem("detailType","addon");
            break;
    }
}
answerForm.addEventListener("submit", (event)=>{
    // event.preventDefault();
    let current_detail=detail.innerText;
    let input_value=input.value;
    sessionStorage.setItem("detail",current_detail);
    sessionStorage.setItem("value",input_value);
    console.log(detailTypeMap[numCurrDetail],detailTypeMap[numCurrDetail+1]);
    setDetailType();
    /* If the question isn't a base question, either skip or confirm depending on input_value
        If it is, either skip 2 or load add-on question depending on input_value
    */
    if(detailTypeMap[numCurrDetail]!="base"){
        if(input_value==""){
            pushToBackendList("null");
            let qVal=getQuestionNum()+1;
            setQuestionNum(qVal);
            answerForm.action="index.html";
        }else{
            // console.log("You entered:",sessionStorage.getItem("value"));
            answerForm.action="confirm.html";
        }
    }else{
        if(input_value==""){
            pushToBackendList("null");
            let qVal=getQuestionNum()+2;
            setQuestionNum(qVal);
            answerForm.action="index.html";
        }else{
            //load the options of the extra question into a session variable
            const options=extraQuestionOptions[numCurrDetail+1].join(",");;
            console.log(options)
            sessionStorage.setItem("options",options);
            sessionStorage.setItem("baseDetail",details[numCurrDetail])
            sessionStorage.setItem("detail",details[numCurrDetail+1]);
            answerForm.action="moreDetails.html";
        }
    }
    answerForm.submit();
})


function loadNextQuestion(qNum){
    console.log("Loaded Next Question");
    //load the next detail
    numCurrDetail=qNum;
    //reset the value of input to load up for the next question
    input.value="";
    //TODO: Add check for if the next detail needed is a moreDetail
    detail.innerText=details[qNum];
    console.log(details[numCurrDetail])
}
//check if this is after the page has been returned to by confirm.html
window.addEventListener("load", (event)=>{
    // console.log("Window loaded");
    let q=getQuestionNum();
    if(q>numCurrDetail){
        loadNextQuestion(q);
    }
    console.log(q,numCurrDetail);
})