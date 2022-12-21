var uploadDropzone;

document.addEventListener('DOMContentLoaded', handleDropzone);

function handleDropzone() {
    uploadDropzone = new Dropzone('div#upload_dropzone', {
        url: `${REQ_CODE}/upload/`,
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

    // append the existing files to the dropzone 
    for (let i=0; i<existing_files.length; i++) {
        let f = existing_files[i];
        uploadDropzone.emit('addedfile', f);
        // uploadDropzone.emit('thumbnail', f, build the blob url)
        uploadDropzone.emit('success', f);
    }
}