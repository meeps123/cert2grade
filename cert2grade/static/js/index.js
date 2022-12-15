function toggleSelectReq(reqEntry) {
    // set checkbox to checked
    if (reqEntry.checked) {
        reqEntry.previousElementSibling.checked = false;
        reqEntry.checked = false;
    } else {
        reqEntry.previousElementSibling.checked = true;
        reqEntry.checked = true;
    }
    // highlight the entry
    reqEntry.classList.toggle('req_entry_wrapper_selected');
}

function reqClick(event, reqEntry) {
    if (event.detail == 1) {
        toggleSelectReq(reqEntry);
    } else if (event.detail == 2) {
        openReq(reqEntry);
    }
}   

function openReq(reqEntry) {
    reqCode = reqEntry.firstElementChild.textContent;
    
}