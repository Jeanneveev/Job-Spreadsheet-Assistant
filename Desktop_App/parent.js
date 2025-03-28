const SERVER_URL = "http://127.0.0.1:5000";

function getQuestionNum(){
    if(sessionStorage.getItem("questionNum")!==null){
        console.log("exists");
        return parseInt(sessionStorage.getItem("questionNum"));
    }else{
        console.log("Doesn't exist");
        sessionStorage.setItem("questionNum","0");    //initializing questionNum for use in passing between pages
        return 0;
    }
}
function setQuestionNum(qVal){
    sessionStorage.removeItem("questionNum");
    sessionStorage.setItem("questionNum",String(qVal));
}
function pushAnswerToBackend(input_value){
    fetch(`${SERVER_URL}/appendAnswer/${input_value}`,{
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
    }).then(response=>response.json()).then((data)=>{
        console.log("You just entered:",data.value);
    })
}
function pushQuestionToBackend(question){
    fetch(`${SERVER_URL}/appendQuestion/${question}`,{
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
    }).then(response=>response.json()).then((data)=>{
        console.log("You just entered:",data.value);
    })
}
export { getQuestionNum, setQuestionNum, pushAnswerToBackend as pushToBackendList, pushQuestionToBackend, SERVER_URL };