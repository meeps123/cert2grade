var dropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);
document.addEventListener('keydown', handleDocumentKeydownForFiles.bind(null, REQ_CODE));
document.addEventListener('click', handleDocumentClickForFiles);

function handleDropzone() {
    filePreviewContainer = document.querySelector('.dropzone');
    deleteFileBtn = document.getElementById('delete_file_btn');

    let churnBtnShown = false;
    
    dropzone = new Dropzone('div#upload_dropzone', {
        url: `${SCRIPT_ROOT}/upload_file/${REQ_CODE}`,
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

    // update the upload status
    document.getElementById('overall_upload_status').textContent = `uploaded ${EXISTING_FILES.length} file${EXISTING_FILES.length == 1 ? '' : 's'}`;

   // init lazy loading just for the files that exist
    dropzone.on('success', observeThumbnail);

    // append the existing files to the dropzone 
    for (let i=0; i<EXISTING_FILES.length; i++) {
        let f = EXISTING_FILES[i];
        dropzone.emit('addedfile', f);
        dropzone.emit('success', f);
        dropzone.emit('complete', f);
        dropzone.emit('uploadprogress', f, 100);
        dropzone.files.push(f);
        f.previewElement.getElementsByClassName('uploaded_size')[0].textContent = Dropzone.prototype.filesize(f['size']);
    }

    // detach old event listeners and arm the dropzone for uploads
    dropzone.off('success', observeThumbnail);
    dropzone.options.autoProcessQueue = true;

    dropzone.on('addedfile', function(f) {
        // hide the churn button and show the abort button
        if (churnBtnShown) {
            churnBtnShown = false;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

        // set the upload status to uploading...
        document.getElementById('overall_upload_status').textContent = 'uploading...';

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
            fetch(`${SCRIPT_ROOT}/upload_thumbnail/${REQ_CODE}`, {
                method: 'POST',
                body: data
            });
        })();
    });
    
    dropzone.on('uploadprogress', (file, progress, bytesSent) => {
        uploadedSizeSpan = file.previewElement.getElementsByClassName('uploaded_size')[0];
        // update the uploaded size
        uploadedSizeSpan.textContent = Dropzone.prototype.filesize(bytesSent - 847);
        // 847 bytes is extra bytes of the metadata that got sent
    });

    dropzone.on('queuecomplete', () => {
        // Run every time after the entire queue is done
        if (!churnBtnShown) {
            churnBtnShown = true;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

        // rebuild the list of file entries
        buildFileEntriesList('dz-complete', REQ_CODE);

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
        data.append('req_code', REQ_CODE);
        data.append('modifications', JSON.stringify(modifications));
        fetch(`${SCRIPT_ROOT}/update_req`, {
            'method': 'POST',
            'body': data
        })
    });

    // ready the abort button
    abortUploadBtn = document.getElementById('abort_upload'); 
    abortUploadBtn.addEventListener('click', abortUpload);
}

function observeThumbnail(f) {
    THUMBNAIL_OBSERVER.observe(f.previewElement.getElementsByTagName('img')[0]);
}

function abortUpload() {
    let uploadingFiles = dropzone.getUploadingFiles(); 
    let uploadingFilenames = [];
    // first remove from the UI
    uploadingFiles.forEach(uploadingFile => {
        dropzone.removeFile(uploadingFile);
        uploadingFilenames.push(uploadingFile.name);
    });

    // then remove the aborted files from the server side
    function deleteAbortedFiles(filenames, counter) {
        if (counter > 3) return;
        let data = new FormData();
        data.append('req_code', REQ_CODE);
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
                
                if (redo) setTimeout(deleteAbortedFiles.bind(null, [filename], counter+1), delay);
            }
        });
    }

    deleteAbortedFiles(uploadingFilenames, 0);
}