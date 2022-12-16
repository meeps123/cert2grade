var lastSelectedEntry;
var allReqEntries = document.getElementsByClassName('req_entry_wrapper');
var sameEntryToggle = false;
var selectedReqMask;
var deleteReqBtn;

document.onselectstart = () => {return false}
document.addEventListener('DOMContentLoaded', () => {
    selectedReqMask = new Array(allReqEntries.length).fill(false);
    deleteReqBtn = document.getElementById('delete_req_btn');
    deleteReqBtn.addEventListener('click', deleteReq);
    let checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    for (let i=0; i<checkboxes.length; i++) {
        checkboxes[i].checked = false;
    }
});
document.addEventListener('keydown', (event) => {
    let e = event || window.event;
    if (e.key == "Escape") clearAll();
});

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

function clearAll() {
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

function reqClick(event, reqEntry) {
    let e = event || window.event;
    if (e.detail == 1) {
        if (e.ctrlKey && e.shiftKey) {
            selectRowsBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(reqEntry)]);
        }
        if (e.ctrlKey) toggleSelectReq(reqEntry);
        if (e.button === 0) {
            if (!e.ctrlKey && !e.shiftKey) {
                if (reqEntry != lastSelectedEntry || sumMask(selectedReqMask) > 1) clearAll();
                toggleSelectReq(reqEntry);
            }
            if (e.shiftKey) {
                selectRowsBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(reqEntry)]);
            }
        }
    } else if (event.detail == 2) {
        openReq(reqEntry);
    }
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
    let url = `${SCRIPT_ROOT}/delete_request`;
    fetch(url, {
        'method': 'POST',
        'body': data
    })
    .then(response => response.json())
    .then(data => {if (data['success']) window.location = SCRIPT_ROOT});
}