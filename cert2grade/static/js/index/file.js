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
        addRemoveLinks: true,
        previewsContainer: 'div#previews',
        uploadMultiple: false,
    });
    indexDropzone.on('addedfile', function(f) {
        // This gets run every time a file is added to the dropzone
        if (!reqCodeCreated) {
            // Create the request
            reqCodeCreated = true;
            fetch(`${SCRIPT_ROOT}/create_req`, {
                'method': 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (!data['success']) alert('failed to create request');
                reqCode = data['code'];
                indexDropzone.options.url = `${SCRIPT_ROOT}/upload/${reqCode}`;
                indexDropzone.options.autoProcessQueue = true;
                indexDropzone.processQueue();
            });
            // render the Uploading UI
            document.getElementById('index_ui').classList.toggle('hidden');
            document.getElementById('upload_ui').classList.toggle('hidden');
        }
    });
    indexDropzone.on('queuecomplete', function(f) {
        // Run every time after the entire queue is done
        if (!churnBtnShown) {
            churnBtnShown = true;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

    });
}