var dropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);
document.addEventListener('keydown', handleDocumentKeydownForFiles.bind(null, REQ_CODE));
document.addEventListener('click', handleDocumentClickForFiles);

function handleDropzone() {
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
}

function observeThumbnail(f) {
    THUMBNAIL_OBSERVER.observe(f.previewElement.getElementsByTagName('img')[0]);
}