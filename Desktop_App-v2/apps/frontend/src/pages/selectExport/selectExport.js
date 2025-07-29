const SERVER_URL = window.electron.SERVER_URL;
const result = document.getElementById("result");
const form = document.getElementById("form");
const submitBtn = document.getElementById("submit");
const backBtn = document.getElementById("back");

/* If CSV is selected enable New and Old options, else, disable them */
const exportOptBtns = document.querySelectorAll('input[name="exportOpt"]');
const csvOpt = document.getElementById("csv");
const newCSV = document.getElementById("new_csv");
const newCSVName = document.getElementById("new_csv_name");
const oldCSV = document.getElementById("old_csv");
const oldCSVFile = document.getElementById("old_csv_file");
exportOptBtns.forEach(exportOptBtn => {
    exportOptBtn.addEventListener("change", () => {
        if(csvOpt.checked) {
            newCSV.disabled = false;
            newCSVName.disabled = false;
            oldCSV.disabled = false;
            oldCSVFile.disabled = false;
            newCSV.required = true;
            oldCSV.required = true;
        } else {
            newCSV.disabled = true;
            newCSVName.disabled = true;
            oldCSV.disabled = true;
            oldCSVFile.disabled = true;
            newCSV.required = false;
            oldCSV.required = false;
        }
    });
});

/* If Name is changed, select New, if file is uploaded, select old */
newCSVName.addEventListener("change", () => {
    if(newCSV.checked == false){
        newCSV.checked = true;
    }
});

oldCSVFile.addEventListener("change", () => {
    if(oldCSV.checked == false){
        oldCSV.checked = true;
    }
});

/* EXPORT */
const setSheetsExport = () => {
    const sheet_id = document.getElementById("sheet_id").value;

    fetch(`${SERVER_URL}/get_auth_url`, { method: "GET" })
        .then(response => response.json()).then(data=>{
            /* Sheets */
            if(data.auth_url){
                //send message to ipcMain to open popup and get code
                window.electron.send("open-auth-window", data.auth_url);
            }else if(data.message){ //a valid token.json exists, so there's no need to reauthenticate, just export
                console.log(data.message);
            }
        })
        .then(() => {
            return fetch(`${SERVER_URL}/set_sheet_id`, {
                method: "POST",
                headers: {
                    "Content-Type": "text/plain"
                },
                body: sheet_id
            })
        })
        .then(response => {
            if (!response.ok){
                const errorText = response.text();
                throw new Error(`Server error: ${response.status}: ${errorText}`);
            }
            return response.text();
        })
        .then(data => console.log(data))
        .then(() => {
            result.innerText = "Google Sheets";
            submitBtn.disabled = false;
            backBtn.disabled = false;
        })
        .catch(error => {
            console.error(error);
            result.innerText = "\nERROR!! Permission Denied\n Try again";
            submitBtn.disabled = false;
        })
}

const setCSVExport = () => {
    const formData = new FormData(form);
    fetch(`${SERVER_URL}/set_export_loc`, {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => console.log(data))
    .then(() => {
            result.innerText = "CSV";
            submitBtn.disabled = false;
            backBtn.disabled = false;
    })
    .catch(error => console.error(error))
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const selectedEl = document.querySelector('input[name="exportOpt"]:checked');  //get the checked option
    const selectedOpt = selectedEl.value;
    result.innerText = "...";
    //disable the submit and back button so that the user can't leave the page before the id's been set
    submitBtn.disabled = true;
    backBtn.disabled = true;

    //set the export method
    fetch(`${SERVER_URL}/set_export_method`, {
        method: "POST",
        headers: {
            "Content-Type": "text/plain"
        },
        body: selectedOpt
    })
    .then(response => response.text())
    .then(data => console.log("set result:", data))
    .catch(error => console.error(error));
    //if the export method is Google Sheets, login the user and set the given id
    if(selectedOpt == "sheets"){
        setSheetsExport();
    } else if(selectedOpt == "csv"){    //if the method is CSV, set up the CSV to be exported to
        setCSVExport();
    }
});

/**
* If a method has already been set, onpageload set the span to the method
* and check the corresponding radio button
*/
window.addEventListener("load", (event)=>{
    fetch(`${SERVER_URL}/get_export_method`,  {method: "GET" })
    .then(response => response.text()).then((data)=>{
        console.log("data:", data);
        if(data != "None"){
            presetOpt = document.getElementById(data);
            presetOptLabel = presetOpt.labels[0].textContent;
            result.innerText = presetOptLabel;
            presetOpt.checked = true;
        }
    });
});