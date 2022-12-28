function readFileAsArrayBufferAsync(file) {
    return new Promise((resolve, reject) => {
        let reader = new FileReader();
        reader.onload = (event) => {
            resolve(event.target.result);
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

async function createThumbnail(file) {
    let contentBuffer = await readFileAsArrayBufferAsync(file);
    const loadingTask = pdfjsLib.getDocument(contentBuffer);
    const pdf = await loadingTask.promise;
    const page = await pdf.getPage(1);
    const scale = 0.1;
    const viewport = page.getViewport({scale});
    const outputScale = window.devicePixelRatio || 1;

    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d');

    canvas.width = Math.floor(viewport.width * outputScale);
    canvas.height = Math.floor(viewport.height * outputScale);

    const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null;
    
    const renderContext = {
        canvasContext: context,
        transform,
        viewport,
    };

    await page.render(renderContext).promise;
    return await new Promise (resolve => canvas.toBlob(resolve));
}

async function getThumbnail(filename) {
    return filename;
}

const THUMBNAIL_OBSERVER = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            (async (thumbnail) => {
                filename = thumbnail.parentElement.firstElementChild.firstElementChild.textContent;
                console.log(await getThumbnail(filename));
            })(entry.target); 
        }
    })
})