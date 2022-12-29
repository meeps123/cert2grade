const CONVERT_SIZE = function(sizeBytes) {
    if (sizeBytes == 0) {
        return '0 B';
    }
    sizeName = ['B', 'KB', 'MB', 'GB', 'TB'];
    i = parseInt(Math.floor(Math.log(sizeBytes)/Math.log(1024)));
    p = Math.pow(1024, i);
    s = Math.round(sizeBytes/p, 2);
    return `${s} ${sizeName[i]}`;
}