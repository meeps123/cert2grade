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
    hasListener = !!deleteFileBtn.getAttribute('data-listener-attached'); 
    if (!hasListener) {
        deleteFileBtn.addEventListener('click', deleteFile.bind(null, reqCode));
        deleteFileBtn.setAttribute('data-listener-attached', true);
    }
    let checkboxes = document.querySelectorAll('input[type=checkbox]:checked');
    for (let i=0; i<checkboxes.length; i++) {
        // set the checkboxes to unchecked
        checkboxes[i].checked = false;
    }
    for (let i=0; i<allFileEntries.length; i++) {
        // set the row index attribute of each file entry
        allFileEntries[i].setAttribute('rowindex', i);
    }
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
        console.log(allowOpenFile);
        // openFile(this);
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
            selectedFiles.push(dropzone.files[i]);
        }
    }
    
    // get list of selected filenames
    selectedFilenames = [];
    selectedFiles.forEach(file => {
        selectedFilenames.push(file.name);
    });

    // delete selected files from the server side
    let data = new FormData();
    data.append('req_code', reqCode);
    data.append('filenames', JSON.stringify(selectedFilenames));
    fetch(`${SCRIPT_ROOT}/delete_file`, {
        'method': 'POST',
        'body': data
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // remove only those files which were successfully deleted on the server side
        for (const [filename, results] of Object.entries(data)) {
            let dbResult = results['database_delete_status'];
            let fileResult = results['file_delete_status'];
            let thumbnailResult = results['thumbnail_delete_status'];
            if ((dbResult == 'success' && fileResult == 'success') && thumbnailResult == 'success') {
                correspondingFile = selectedFiles.filter((f) => {return f.name == filename})[0];
                dropzone.removeFile(correspondingFile);
            } 
        }
        dropzone.emit('queuecomplete');
        updateDeleteFileBtn();
    });
}