import { getQuestionNum,setQuestionNum,pushToBackendList } from "./parent.js"
const passedDetail=sessionStorage.getItem("detail");
const passedValue=sessionStorage.getItem("value");
const detailSpan=document.getElementById("detail");
const valueSpan=document.getElementById("value");
detailSpan.innerText=passedDetail;
valueSpan.innerText=passedValue;

const confirmationForm=document.getElementById("confirm");
const yesBtn=document.getElementById("yes");
var q=getQuestionNum();
confirmationForm.addEventListener("submit", (event)=>{
    // event.preventDefault();
    if(event.submitter==yesBtn){
        // pushToBackendList(passedValue);
        q+=1;
        setQuestionNum(q);
    }
    confirmationForm.action="index.html";
    confirmationForm.submit();
})