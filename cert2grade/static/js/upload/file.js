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
    document.getElementById('overall_upload_status').textContent = `uploaded ${existing_files.length} file${existing_files.length == 1 ? '' : 's'}`;

   // init lazy loading just for the files that exist
    dropzone.on('success', (f) => {
        THUMBNAIL_OBSERVER.observe(f.previewElement.getElementsByTagName('img')[0])
    })

    // append the existing files to the dropzone 
    for (let i=0; i<existing_files.length; i++) {
        let f = existing_files[i];
        dropzone.emit('addedfile', f);
        dropzone.emit('success', f);
        dropzone.emit('complete', f);
        dropzone.files.push(f);
    }

    // detach lazy loading and arm the dropzone for uploads
    dropzone.off('success');
    dropzone.options.autoProcessQueue = true;

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