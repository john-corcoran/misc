// Run in browser developer console on an Internet Archive JSON metadata page, e.g. https://archive.org/metadata/gov.archives.arc.1155023

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

var item_metadata = JSON.parse(document.body.textContent);
var files_metadata = item_metadata.files;
var file_list_length = files_metadata.length;
var total_size = 0;

for (var i = 0; i < file_list_length; i++) {
    file_metadata = files_metadata[i];
    file_size = file_metadata.size;
    if (file_size == undefined) {
        file_size = 0;
    }
    total_size += Number(file_size);
}

console.log(formatBytes(total_size) + " (" + total_size + " bytes)");
