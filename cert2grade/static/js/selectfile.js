var filePreviewContainer;
var lastSelectedEntry;
var allFileEntries = []; 
var selectedFileMask = [];
var deleteFileBtn;

function handleDocumentKeydownForFiles(event) {
    let e = event || window.event;
    if (e.key == 'Escape') clearAllFiles();
    if (e.key == 'Delete') deleteFile();
}

function handleDocumentClickForFiles(event) {
    let e = event || window.event;
    if (!filePreviewContainer.contains(e.target)) clearAllFiles();
}

function buildFileEntriesList(classToSearch) {
    allFileEntries = document.getElementsByClassName(classToSearch);
    selectedFileMask = new Array(allFileEntries.length).fill(false);
    deleteFileBtn = document.getElementById('delete_file_btn');
    deleteFileBtn.addEventListener('click', deleteFile);
    let checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    for (let i=0; i<checkboxes.length; i++) {
        // set the checkboxes to unchecked
        checkboxes[i].checked = false;
    }
    for (let i=0; i<allFileEntries.length; i++) {
        // set the row index attribute of each file entry
        allFileEntries[i].setAttribute('rowindex', i);
    }
    filePreviewContainer = document.getElementById('index_dropzone');
}

function rowIndex(fileEntry) {
    return parseInt(fileEntry.getAttribute('rowindex'));
}

function toggleSelectFile(fileEntry) {
    fileEntry.children[1].checked = !fileEntry.children[1].checked;
    fileEntry.classList.toggle('file_entry_selected');
    selectedFileMask[rowIndex(fileEntry)] = !selectedFileMask[rowIndex(fileEntry)];
    lastSelectedEntry = fileEntry;
    updateDeleteFileBtn();
}

function clearAllFiles() {
    for (let i=0; i<allFileEntries.length; i++) {
        allFileEntries[i].classList.remove('file_entry_selected');
        allFileEntries[i].children[1].checked = false;
    }
    selectedFileMask.fill(false);
    updateDeleteFileBtn();
}

function selectFilesBetweenIndices(indices) {
    indices.sort((a, b) => {return a - b});
    selectedFileMask.fill(true, indices[0], indices[1]+1);
    for (let i=indices[0]; i<=indices[1]; i++) {
        allFileEntries[i].classList.add('file_entry_selected');
        allFileEntries[i].children[1].checked = true;
    }
    updateDeleteFileBtn();
}

function fileClick(event, fileEntry, allowOpenFile=false) {
    let e = event || window.event;
    console.log(fileEntry);
    if (e.detail == 1) {
        if (e.ctrlKey && e.shiftKey) {
            selectFilesBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(fileEntry)]);
        }
        if (e.ctrlKey) toggleSelectFile(fileEntry);
        if (e.button === 0) {
            if (!e.ctrlKey && !e.shiftKey) {
                if (fileEntry != lastSelectedEntry || sumMask(selectedFileMask) > 1) clearAllFiles();
                toggleSelectFile(fileEntry);
            }
            if (e.shiftKey) {
                selectFilesBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(fileEntry)]);
            }
        }
    } else if (event.detail == 2 && allowOpenFile) {
        openFile(fileEntry);
    }
}

function sumMask(mask) {
    return mask.reduce((a,b)=>a+b,0)
}

function updateDeleteFileBtn() {
    total = sumMask(selectedFileMask);
    if (total) {
        deleteFileBtn.classList.remove('hidden');
        deleteFileBtn.textContent = `delete ${total} entr${(total == 1) ? 'y' : 'ies'}`;
    } else {
        deleteFileBtn.classList.add('hidden'); 
    }
}

function openFile(fileEntry) {
    reqCode = fileEntry.firstElementChild.textContent;
    window.location = `${SCRIPT_ROOT}/req/${encodeURIComponent(reqCode)}`;
}

function deleteFile() {
    // selectedReqCodes = [];
    // for (let i=0; i<allFileEntries.length; i++) {
    //     if (selectedFileMask[i]) {
    //         code = allFileEntries[i].firstElementChild.textContent;
    //         selectedReqCodes.push(code);
    //     }
    // }
    // let data = new FormData();
    // data.append('req_codes', selectedReqCodes.join('|'));
    // fetch(`${SCRIPT_ROOT}/delete_req`, {
    //     'method': 'POST',
    //     'body': data
    // })
    // .then(response => response.json())
    // .then(data => {
    //     if (!data['success']) alert(`error deleting ${total} entr${(total == 1) ? 'y' : 'ies'}`);
    //     window.location = SCRIPT_ROOT;
    // });
}