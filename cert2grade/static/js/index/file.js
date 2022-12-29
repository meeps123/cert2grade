var dropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);

function handleDropzone() {
    filePreviewContainer = document.querySelector('.dropzone');
    deleteFileBtn = document.getElementById('delete_file_btn');
    
    let reqCode;
    let reqCodeCreated = false;
    let churnBtnShown = false;
    
    dropzone = new Dropzone('div#index_dropzone', {
        url: `${SCRIPT_ROOT}/upload/`, // we will add the request code later
        clickable: true,
        chunking: true,
        forceChunking: true,
        retryChunks: true,
        parallelChunkUploads: 10,
        acceptedFiles: 'application/pdf',
        autoProcessQueue: false,
        previewTemplate: document.getElementById('preview_template').innerHTML,
        uploadMultiple: false,
    });
    dropzone.on('addedfile', function(f) {
        // This gets run every time a file is added to the dropzone
    
        // hide the churn button and show the abort button
        if (churnBtnShown) {
            churnBtnShown = false;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

        // set the upload status to uploading...
        document.getElementById('overall_upload_status').textContent = 'uploading...';

        // Create the request once only
        if (!reqCodeCreated) {
            reqCodeCreated = true;
            fetch(`${SCRIPT_ROOT}/create_req`, {
                'method': 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (!data['success']) alert('failed to create request');
                reqCode = data['code'];
                dropzone.options.url = `${SCRIPT_ROOT}/upload_file/${reqCode}`;
                dropzone.options.autoProcessQueue = true;
                dropzone.processQueue();
                // attach the new event listeners for file selection once only
                document.addEventListener('keydown', handleDocumentKeydownForFiles.bind(null, reqCode));
                document.addEventListener('click', handleDocumentClickForFiles);
                // set the req code at the top of page
                document.getElementById('req_code').textContent = `#${reqCode}`;
                // attach the event listener for file upload abort
                abortUploadBtn = document.getElementById('abort_upload'); 
                abortUploadBtn.classList.remove('hidden');
                abortUploadBtn.addEventListener('click', abortUpload.bind(abortUploadBtn, reqCode));
            });
            // render the uploading UI once only
            document.getElementById('index_ui').remove();
            document.getElementById('dropzone_prompt').remove();
            document.getElementById('upload_ui').classList.toggle('hidden');
            // detach the event listeners for request selection once only
            document.removeEventListener('keydown', handleDocumentKeydownForReqs);
            document.removeEventListener('click', handleDocumentClickForReqs);
        }

        // create the BLOB thumbnail of the pdf
        // upload the thumbnail to the server
        (async () => {
            blob = await createThumbnail(f);
            dataURL = URL.createObjectURL(blob);
            dropzone.emit('thumbnail', f, dataURL);
            thumbnail_file = new File([blob], `${f.name.split('.')[0]}_thumbnail.png`, {
                type: 'image/png'
            });
            let data = new FormData();
            data.append('file', thumbnail_file);       
            fetch(`${SCRIPT_ROOT}/upload_thumbnail/${reqCode}`, {
                method: 'POST',
                body: data
            });
        })();
    });
    dropzone.on('queuecomplete', () => {
        // Run every time after the entire queue is done
        if (!churnBtnShown) {
            churnBtnShown = true;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

        // rebuild the list of file entries
        buildFileEntriesList('dz-complete', reqCode);

        // update the header to show how mamy files uploaded
        document.getElementById('overall_upload_status').textContent = `uploaded ${dropzone.files.length} file${dropzone.files.length == 1 ? '' : 's'}`;

        // update the request metadata in the database
        totalReqSize = 0;
        totalReqFiles = dropzone.files.length;
        for (let i=0; i<totalReqFiles; i++) {
            totalReqSize += dropzone.files[i].size;
            // at the same time add the onclick listeners to the file previews to enable selection
            previewElement = dropzone.files[i].previewElement;
            hasListener = !!previewElement.getAttribute('data-listener-attached'); 
            if (!hasListener) {
                previewElement.addEventListener('click', fileClick.bind(previewElement, false));
                previewElementCheckbox = previewElement.children[1];
                previewElementCheckbox.addEventListener('click', fileCheckboxClick.bind(previewElementCheckbox));
                previewElement.setAttribute('data-listener-attached', true);
            }
          }
        let modifications = {
            'files': totalReqFiles,
            'size': totalReqSize
        }
        let data = new FormData();
        data.append('req_code', reqCode);
        data.append('modifications', JSON.stringify(modifications));
        fetch(`${SCRIPT_ROOT}/update_req`, {
            'method': 'POST',
            'body': data
        })
    });
    dropzone.on('uploadprogress', (file, progress, bytesSent) => {
        uploadedSizeSpan = file.previewElement.getElementsByClassName('uploaded_size')[0];
        // update the uploaded size
        uploadedSizeSpan.textContent = Dropzone.prototype.filesize(bytesSent - 847);
        // 847 bytes is extra bytes of the metadata that got sent
    });
}

function abortUpload(reqCode) {
    let uploadingFiles = dropzone.getUploadingFiles(); 
    let uploadingFilenames = [];
    // first remove from the UI
    uploadingFiles.forEach(uploadingFile => {
        dropzone.removeFile(uploadingFile);
        uploadingFilenames.push(uploadingFile.name);
    });

    // then remove the aborted files from the server side
    function deleteAbortedFiles(reqCode, filenames, counter) {
        if (counter > 3) return;
        let data = new FormData();
        data.append('req_code', reqCode);
        data.append('filenames', JSON.stringify(filenames));
        fetch(`${SCRIPT_ROOT}/delete_file`, {
            'method': 'POST',
            'body': data
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            for (const [filename, results] of Object.entries(data)) {
                let dbResult = results['database_delete_status'];
                let fileResult = results['file_delete_status'];
                let thumbnailResult = results['thumbnail_delete_status'];
                let redo = false;
                let delay = 0;
                if (dbResult == 'success' && (fileResult == 'pdf_not_in_filesystem' || thumbnailResult == 'thumbnail_not_in_filesystem')) {
                    // an entry in the db was deleted but somehow couldn't find the pdf or the thumbnail
                    // this is a sign that the upload of the pdf and the thumbnail is still in progress
                    redo = true;
                    delay = 1000;
                }
                if (fileResult == 'success' && thumbnailResult == 'thumbnail_not_in_filesystem') {
                    // the pdf was deleted but couldn't find the thumbnail
                    // highly likely that thumbnail upload is still in progress
                    redo = true;
                    delay = 1000;
                }
                if (dbResult == 'entry_not_in_db' && (thumbnailResult == 'thumbnail_not_in_filesystem' && fileResult == 'pdf_not_in_filesystem')) {
                    // everything cannot be found
                    // either that really everything has been deleted
                    // or that the abort managed to stop the pdf upload and the writing to db, but not the upload of thumbnail
                    redo = true;
                }
                if (dbResult == 'entry_not_in_db' && (fileResult == 'success' || thumbnailResult == 'success')) {
                    // managed to delete pdf or thumbnail, but couldnt find in db
                    // maybe the deletion occurred halfway between writing of file and writing of db entry
                    // retry to be sure
                    redo = true; 
                }
                
                if (redo) setTimeout(deleteAbortedFiles.bind(null, reqCode, [filename], counter+1), delay);
            }
        });
    }

    deleteAbortedFiles(reqCode, uploadingFilenames, 0);
}