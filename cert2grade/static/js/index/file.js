var indexDropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);

function handleDropzone() {
    let reqCode;
    let reqCodeCreated = false;
    let churnBtnShown = false;
    indexDropzone = new Dropzone('div#index_dropzone', {
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
    indexDropzone.on('addedfile', function(f) {
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
                indexDropzone.options.url = `${SCRIPT_ROOT}/upload_file/${reqCode}`;
                indexDropzone.options.autoProcessQueue = true;
                indexDropzone.processQueue();
                // attach the new event listeners for file selection once only
                document.addEventListener('keydown', handleDocumentKeydownForFiles.bind(null, reqCode));
                document.addEventListener('click', handleDocumentClickForFiles);
                // set the req code at the top of page
                document.getElementById('req_code').textContent = `#${reqCode}`;
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
            indexDropzone.emit('thumbnail', f, dataURL);
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
    indexDropzone.on('queuecomplete', () => {
        // Run every time after the entire queue is done
        if (!churnBtnShown) {
            churnBtnShown = true;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

        // rebuild the list of file entries
        buildFileEntriesList('dz-complete', reqCode);

        // update the header to show how mamy files uploaded
        document.getElementById('overall_upload_status').textContent = `uploaded ${indexDropzone.files.length} file${indexDropzone.files.length == 1 ? '' : 's'}`;

        // update the request metadata in the database
        totalReqSize = 0;
        totalReqFiles = indexDropzone.files.length;
        for (let i=0; i<totalReqFiles; i++) {
            totalReqSize += indexDropzone.files[i].size;
            // at the same time add the onclick listeners to the file previews to enable selection
            previewElement = indexDropzone.files[i].previewElement;
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
}