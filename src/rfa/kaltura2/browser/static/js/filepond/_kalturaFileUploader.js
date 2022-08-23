function cleanupStyle() {
    const el = document.querySelector('.filepond--credits');
    el.style.display = 'none';
}

function appendStyle() {
    const link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = "++plone++rfa.kaltura2/css/filepond.min.css";
    document.head.appendChild(link);
}

require([
    "++plone++rfa.kaltura2/js/filepond.min.js",
    "++plone++rfa.kaltura2/js/filepond-plugin-file-validate-size.js",
    "++plone++rfa.kaltura2/js/filepond-plugin-file-validate-type.js"],
    (FilePond, FilePondPluginFileValidateSize, FilePondPluginFileValidateType) => {

        appendStyle();

        const inputElement = document.getElementById('kalturaInput');

        FilePond.registerPlugin(FilePondPluginFileValidateSize);
        FilePond.registerPlugin(FilePondPluginFileValidateType);

        const pond = FilePond.create(inputElement);
        cleanupStyle();

        pond.setOptions({
            maxFiles: 1,
            required: true,
            allowDrop: false,
            instantUpload: false,
            maxFileSize: '2000MB',
            // acceptedFileTypes: ['video/*'],
            chunkUploads: true,
            chunkSize: 10000000,
            chunkForce: false,
            chunkRetryDelays: [500, 1000, 3000],
            server: {
                url: './',
                timeout: 7000,
                process: {
                    url: '',
                    method: 'POST',
                    headers: {
                        'x-customheader': 'Hello World',
                    },
                    withCredentials: false,
                    onload: (response) => console.log(response),
                    onerror: (response) => console.log(response),
                    ondata: (formData) => console.log(formData),
                },
                // patch: {
                //     url: '/'
                // },
            },
        })
    });
