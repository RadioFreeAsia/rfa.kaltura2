let KALTURA_SESSION_TOKEN = '';

function appendStyle(url) {
    const link = document.createElement("link");
    link.type = "text/css";
    link.rel = "stylesheet";
    link.href = url;
    document.head.appendChild(link);
}



async function getKsToken() {
    const responce = await fetch('./getKs');
    const data = await responce.json();
    KALTURA_SESSION_TOKEN = data.ks;
}

appendStyle('++plone++rfa.kaltura2/css/jquery.fileupload-ui.css');
appendStyle('++plone++rfa.kaltura2/css/jquery.fileupload-ui-kaltura.css');
appendStyle('++plone++rfa.kaltura2/css/style.css');

getKsToken();

require([
    "++plone++rfa.kaltura2/js/jquery.ui.widget.js",
    "++plone++rfa.kaltura2/js/jquery.iframe-transport.js",
    "++plone++rfa.kaltura2/js/webtoolkit.md5.js",
    "++plone++rfa.kaltura2/js/jquery.fileupload.js",
    "++plone++rfa.kaltura2/js/jquery.fileupload-process.js",
    "++plone++rfa.kaltura2/js/jquery.fileupload-validate.js",
    "++plone++rfa.kaltura2/js/jquery.fileupload-kaltura.js",
    "++plone++rfa.kaltura2/js/jquery.fileupload-kaltura-base.js",
], function (
    widget,
    frameTransport,
    webtoolkit,
    fileupload,
    fileuploadProcess,
    fileuploadValidate,
    fileuploadKaltura,
    fileuploadKalturaBase
) {

    // runs when the video already exists
    if ($('#upload-token-container > input').val().length) {

        $('#fileuploadBtn').text('Click here to upload a new file');
        $('#fileuploadBtn').click(() => {
            $('#upload-token-container > input').val('');
        })

        $.ajax({
            url: `https://www.kaltura.com/api_v3/service/uploadtoken/action/get?
            ks=${KALTURA_SESSION_TOKEN}&format=1`,
            data: { uploadTokenId: $('#upload-token-container > input').val() },
            type: "POST",
            dataType: 'json'
        }).done((response) => {
            $(`<span class='warningMsg'>
                    You already have a file selected: 
                    <strong>${response.fileName}</strong>
                </span>`)
            .insertBefore("#uploadbutton");
        });
    }

    const categoryId = -1;

    widget = $('#uploadHook').fileupload({
        maxChunkSize: 10000000,
        dynamicChunkSizeInitialChunkSize: 10000000,
        dynamicChunkSizeThreshold: 50000000,
        dynamixChunkSizeMaxTime: 30,
        host: "https://www.kaltura.com",
        apiURL: "https://www.kaltura.com/api_v3/",
        url: "https://www.kaltura.com/api_v3/?service=uploadToken&action=upload&format=1",
        ks: KALTURA_SESSION_TOKEN,
        fileTypes: `*.mts;*.MTS;*.qt;*.mov;*.mpg;*.avi;*.m4a;*.mp4;
        *.wma;*.vob;*.flv;*.f4v;*.asf;*.qt;*.mov;*.mpeg;*.avi;*.wmv;*.m4v;*.3gp;
        *.mkv;*.QT;*.MOV;*.MPG;*.AVI;*.M4A;*.WAV;*.MP4;*.WMA;*.VOB;*.FLV;*.F4V;*.ASF;*.QT;*.MOV;*.MPEG;
        *.AVI;*.WMV;*.M4V;*.3GP;*.MKV;*.webm;*.WEBM;
        *.AIFF;*.arf;*.ARF;*.rm;*.RM;*.ra;*.RA;*.RV;*.rv;*.aiff`,
        context: '',
        categoryId: categoryId,
        messages: {
            acceptFileTypes: 'File type not allowed',
            maxFileSize: 'File is too large',
            minFileSize: 'File is too small'
        },
        android: "",
        singleUpload: "true"
    })
        // file added
        .bind('fileuploadadd', function (e, data) {
            console.log('fileuploaded');
            const uploadBoxId = widget.fileupload('getUploadBoxId', e, data);
            data.uploadBoxId = uploadBoxId;
            const uploadManager = widget.fileupload("getUploadManager");
            if (!uploadManager.hasWidget($(this)) && !widget.fileupload('option', 'android') && !widget.fileupload('option', 'singleUpload')) {
                // load the next uploadbox (anyway even if there is an error)
                widget.fileupload('addUploadBox', e, data);
            }
        })
        // actual upload start
        .bind('fileuploadsend', function (e, data) {
            console.log('fileuploadsend');
            const uploadBoxId = widget.fileupload('getUploadBoxId', e, data);
            const file = data.files[0];
            const uploadManager = widget.fileupload("getUploadManager");
            $('#fileuploadBtn').attr('disabled', '');

            if (file.error === undefined) {
                const context = widget.fileupload('option', 'context');
                console.log('upload context: ' + context);
                console.log('now uploading file name: ' + encodeURIComponent(file.name));
                //here we should display an edit entry form to allow the user to add/save metadata to the entry
                $("#uploadbox" + uploadBoxId + " .entry_details").removeClass('hidden');
            } else {
                console.log('some kind of error when starting to upload ' + file.error);
            }
        })
        // upload done
        .bind('fileuploaddone', function (e, data) {
            console.log('fileuploaddone');
            console.log('fileuploaddone');
            const uploadBoxId = widget.fileupload('getUploadBoxId', e, data);
            const file = data.files[0];

            $('#upload-file-info').addClass('hidden');
            $('.successFileName').text('Successfully uploaded file: ' + file.name);
            $('#upload-token-container > input').val(data.uploadTokenId);
        })
        // upload error
        .bind('fileuploaderror', function (e, data) {
            console.log('fileuploaderror');
            const uploadBoxId = widget.fileupload('getUploadBoxId', e, data);
            const uploadBox = widget.fileupload('getUploadBox', uploadBoxId);
            $("#entry_details", uploadBox).addClass('hidden');
            if (widget.fileupload('option', 'singleUpload')) {
                // load the next uploadbox (if an error occured and it's a single upload do not cause a dead end for the user)
                widget.fileupload('addUploadBox', e, data);
            }
        })
        // upload cancelled
        .bind('fileuploadcancel', function (e, data) {
            console.log('fileuploadcancel');
            const uploadBoxId = widget.fileupload('getUploadBoxId', e, data);
            const uploadBox = widget.fileupload('getUploadBox', uploadBoxId);
            $("#entry_details", uploadBox).addClass('hidden');
            $('#fileuploadBtn').removeAttr('disabled');
        });

    // bind to the first upload input
    $("#uploadbox1 #fileinput").bind('change', function (e) {
        $('#uploadHook').fileupload('add', {
            fileInput: $(this),
            uploadBoxId: 1
        });
        console.log('file chosen');
        $('#fileuploadBtn').attr('disabled', '');
    });
});
