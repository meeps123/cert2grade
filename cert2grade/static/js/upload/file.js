var uploadDropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);

function handleDropzone() {
    uploadDropzone = new Dropzone('div#upload_dropzone', {
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
    uploadDropzone.on('success', (f) => {
        THUMBNAIL_OBSERVER.observe(f.previewElement.getElementsByTagName('img')[0])
    })

    // append the existing files to the dropzone 
    for (let i=0; i<existing_files.length; i++) {
        let f = existing_files[i];
        uploadDropzone.emit('addedfile', f);
        uploadDropzone.emit('success', f);
    }


}