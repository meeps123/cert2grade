var filePreviewContainer;
var lastSelectedEntry;
var allFileEntries = []; 
var selectedFileMask = [];
var deleteFileBtn;

function handleDocumentKeydownForFiles(reqCode) {
    let e = event || window.event;
    if (e.key == 'Escape') clearAllFiles();
    if (e.key == 'Delete') deleteFile(reqCode);
}

function handleDocumentClickForFiles() {
    let e = event || window.event;
    if (!filePreviewContainer.contains(e.target)) clearAllFiles();
}

function buildFileEntriesList(classToSearch, reqCode) {
    allFileEntries = document.getElementsByClassName(classToSearch);
    selectedFileMask = new Array(allFileEntries.length).fill(false);
    deleteFileBtn = document.getElementById('delete_file_btn');
    deleteFileBtn.addEventListener('click', deleteFile.bind(null, reqCode));
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

function fileClick(allowOpenFile=false) {
    let e = event || window.event;
    if (e.detail == 1) {
        if (e.ctrlKey && e.shiftKey) {
            selectFilesBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(this)]);
        }
        if (e.ctrlKey) toggleSelectFile(this);
        if (e.button === 0) {
            if (!e.ctrlKey && !e.shiftKey) {
                if (this != lastSelectedEntry || sumMask(selectedFileMask) > 1) clearAllFiles();
                toggleSelectFile(this);
            }
            if (e.shiftKey) {
                selectFilesBetweenIndices([rowIndex(lastSelectedEntry), rowIndex(this)]);
            }
        }
    } else if (e.detail == 2 && allowOpenFile) {
        openFile(this);
    }
}

function fileCheckboxClick() {
    this.checked = !this.checked;
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

function deleteFile(reqCode) {
    // get all selected files
    selectedFiles = [];
    for (let i=0; i<allFileEntries.length; i++) {
        if (selectedFileMask[i]) {
            selectedFiles.push(indexDropzone.files[i]);
        }
    }
    
    // get list of selected filenames
    selectedFilenames = [];
    selectedFiles.forEach(file => {
        selectedFilenames.append(file.name);
    });

    // delete selected files from the server side
    let data = new FormData();
    data.append('req_code', reqCode);
    data.append('filenames', selectedFilenames);
    fetch(`${SCRIPT_ROOT}/delete_file`, {
        'method': 'POST',
        'body': data
    })
    .then(response => response.json())
    .then(data => {
        // remove only those files which were successfully deleted on the server side
        console.log(data);
    });
}