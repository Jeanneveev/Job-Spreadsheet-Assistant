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
    "JOB LOCATION", "NAME OF THE SITE THE JOB WAS FOUND ON", "LINK TO WHERE THE JOB WAS FOUND",
    "SALARY"
]
const moreDetails=["job_loc_type","salary_type"];
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


function loadNextQuestion(){
    //load the next detail
    numCurrDetail+=1;
    //reset the value of input to load up for the next question
    input.value="";
    //TODO: Add check for if the next detail needed is a moreDetail
    detail.innerText=details[numCurrDetail];
}

answerForm.addEventListener("submit", (event)=>{
    // event.preventDefault();
    let current_detail=detail.innerText;
    let input_value=input.value;
    //handle skip
    if(input_value==""){
        console.log("ADD SKIP FUNCTIONALITY");
    }else{
        sessionStorage.setItem("detail",current_detail);
        sessionStorage.setItem("value",input_value);
        // console.log("You entered:",sessionStorage.getItem("value"));
    }
    answerForm.action="confirm.html";
    answerForm.submit();
})



//check if this is after the page has been returned to by confirm.html
window.addEventListener("load", (event)=>{
    let q=getQuestionNum();
    if(q>numCurrDetail){
        loadNextQuestion();
    }
    console.log(q,numCurrDetail);
})