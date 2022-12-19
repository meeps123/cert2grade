var indexDropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);


function handleDropzone() {
    let reqCode;
    let reqCodeCreated = false;
    indexDropzone = new Dropzone('div#index_dropzone', {
        url: `${SCRIPT_ROOT}/upload/`, // we will add the request code later
        clickable: true,
        chunking: true,
        forceChunking: true,
        retryChunks: true,
        parallelChunkUploads: 10,
        
        autoProcessQueue: false,
        addRemoveLinks: true
    });
    indexDropzone.on('addedfile', (f) => {
        // Create the request if not created already
        if (!reqCodeCreated) {
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
        }
    });
}