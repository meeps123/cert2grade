var reqHistoryDiv;
var lastSelectedEntry;
var allReqEntries = document.getElementsByClassName('req_entry_wrapper');
var selectedReqMask;
var deleteReqBtn;

document.onselectstart = () => {return false} // prevents text selection
document.addEventListener('DOMContentLoaded', () => {
    selectedReqMask = new Array(allReqEntries.length).fill(false);
    deleteReqBtn = document.getElementById('delete_req_btn');
    deleteReqBtn.addEventListener('click', deleteReq);
    let checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    for (let i=0; i<checkboxes.length; i++) {
        checkboxes[i].checked = false;
    }
    reqHistoryDiv = document.getElementById('req_history');
    let durationCells = document.querySelectorAll('div.req_duration');
    durationCells.forEach(durationCell => {
        switch (durationCell.textContent) {
            case 'awaiting user input':
                durationCell.parentElement.classList.add('awaiting');
                break;
            case 'in progress':
                durationCell.parentElement.classList.add('in_progress');
                break;
            default:
                break;
        }
    });
});
document.addEventListener('keydown', handleDocumentKeydownForReqs);
document.addEventListener('click', handleDocumentClickForReqs);

function handleDocumentKeydownForReqs(event) {
    let e = event || window.event;
    if (e.key == 'Escape') clearAllReqs();
    if (e.key == 'Delete') deleteReq();
}

function handleDocumentClickForReqs(event) {
    let e = event || window.event;
    if (!reqHistoryDiv.contains(e.target)) clearAllReqs();    
}

function rowIndex(reqEntry) {
    return parseInt(reqEntry.getAttribute('rowindex'));
}

function toggleSelectReq(reqEntry) {
    reqEntry.previousElementSibling.checked = !reqEntry.previousElementSibling.checked;
    reqEntry.parentElement.classList.toggle('req_entry_row_selected');
    selectedReqMask[rowIndex(reqEntry)] = !selectedReqMask[rowIndex(reqEntry)];
    lastSelectedEntry = reqEntry;
    updateDeleteReqBtn();
}

function clearAllReqs() {
    for (let i=0; i<allReqEntries.length; i++) {
        allReqEntries[i].parentElement.classList.remove('req_entry_row_selected');
        allReqEntries[i].previousElementSibling.checked = false;
    }
    selectedReqMask.fill(false);
    updateDeleteReqBtn();
}

function selectRowsBetweenIndices(indices) {
    indices.sort((a, b) => {return a - b});
    selectedReqMask.fill(true, indices[0], indices[1]+1);
    console.log(selectedReqMask);
    for (let i=indices[0]; i<=indices[1]; i++) {
        allReqEntries[i].parentElement.classList.add('req_entry_row_selected');
        allReqEntries[i].previousElementSibling.checked = true;
    }
    updateDeleteReqBtn();
}

function reqClick(fromCheckbox=false) {
    let e = event || window.event;
    if (e.detail == 1 || fromCheckbox) {
        if (e.ctrlKey && e.shiftKey) {
            selectRowsBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(this)]);
        }
        if (e.ctrlKey) toggleSelectReq(this);
        if (e.button === 0 || fromCheckbox) {
            if (!e.ctrlKey && !e.shiftKey) {
                if (this != lastSelectedEntry || sumMask(selectedReqMask) > 1) clearAllReqs();
                toggleSelectReq(this);
            }
            if (e.shiftKey) {
                selectRowsBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(this)]);
            }
        }
    } else if (e.detail == 2) {
        openReq(this);
    }
}

function reqCheckboxClick() {
    this.checked = !this.checked;
    reqClick.call(this.nextElementSibling, true);
}

function sumMask(mask) {
    return mask.reduce((a,b)=>a+b,0)
}

function updateDeleteReqBtn() {
    total = sumMask(selectedReqMask);
    if (total) {
        deleteReqBtn.classList.remove('hidden');
        deleteReqBtn.textContent = `delete ${total} entr${(total == 1) ? 'y' : 'ies'}`;
    } else {
        deleteReqBtn.classList.add('hidden'); 
    }
}

function openReq(reqEntry) {
    reqCode = reqEntry.firstElementChild.textContent;
    window.location = `${SCRIPT_ROOT}/req/${encodeURIComponent(reqCode)}`;
}

function deleteReq() {
    selectedReqCodes = [];
    for (let i=0; i<allReqEntries.length; i++) {
        if (selectedReqMask[i]) {
            code = allReqEntries[i].firstElementChild.textContent;
            selectedReqCodes.push(code);
        }
    }
    let data = new FormData();
    data.append('req_codes', selectedReqCodes.join('|'));
    fetch(`${SCRIPT_ROOT}/delete_req`, {
        'method': 'POST',
        'body': data
    })
    .then(response => response.json())
    .then(data => {
        if (!data['success']) alert(`error deleting ${total} entr${(total == 1) ? 'y' : 'ies'}`);
        window.location = SCRIPT_ROOT;
    });
}