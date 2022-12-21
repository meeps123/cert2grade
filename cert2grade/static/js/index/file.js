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
        previewsContainer: 'div#previews',
        previewTemplate: document.getElementById('preview_template').innerHTML,
        uploadMultiple: false,
    });
    indexDropzone.on('addedfile', function(f) {
        // This gets run every time a file is added to the dropzone
        if (!reqCodeCreated) {
            // Create the request once only
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
            // render the Uploading UI once only
            document.getElementById('index_ui').remove();
            document.getElementById('upload_ui').classList.toggle('hidden');
        }
        // create the BLOB thumbnail of the pdf
        // upload the thumbnail to the server
        (async () => {
            blob = await getThumbnail(f);
            indexDropzone.emit('thumbnail', f, URL.createObjectURL(blob));
            thumbnail_file = new File([blob], `${f.name.split('.')[0]}_thumbnail.png`, {
                type: 'image/png'
            });
            let data = new FormData();
            data.append('file', thumbnail_file);       
            console.log(reqCode);
            fetch(`${SCRIPT_ROOT}/upload_thumbnail/${reqCode}`, {
                method: 'POST',
                body: data
            })
        })();
    });
    indexDropzone.on('queuecomplete', function(f) {
        // Run every time after the entire queue is done
        if (!churnBtnShown) {
            churnBtnShown = true;
            document.getElementById('abort_upload').classList.toggle('hidden');
            document.getElementById('start_churn').classList.toggle('hidden');
        }

        // update the request metadata in the database
        totalReqSize = 0;
        totalReqFiles = indexDropzone.files.length;
        for (let i=0; i<totalReqFiles; i++) {
            totalReqSize += indexDropzone.files[i].size;
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