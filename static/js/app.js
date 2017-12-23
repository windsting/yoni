$(function () {

    var fileUploadSuccess = function (data) {
        console.log(data);
        if (data)
            $('#resultarea').html('<img id="theImg" src="' + data + '" />')
    };

    var fileUploadFail = function (data) {
        console.log("fileUploadFail");
        console.log(data);
    };

    var dragHandler = function (evt) {
        evt.preventDefault();
    };

    var dropHandler = function (evt) {
        evt.preventDefault();
        var files = evt.originalEvent.dataTransfer.files;

        var file = files[0];
        var fileType = file["type"];
        var ValidImageTypes = ["image/gif", "image/jpeg", "image/png"];
        if ($.inArray(fileType, ValidImageTypes) < 0) {
            // invalid file type code goes here.
            console.log("Don't joke, only image accepted!");
            return;
        }

        var formData = new FormData();
        formData.append("file2upload", files[0]);

        var req = {
            url: "/sendfile",
            method: "post",
            processData: false,
            contentType: false,
            data: formData
        };

        var promise = $.ajax(req);
        promise.then(fileUploadSuccess, fileUploadFail);
    };

    var dropHandlerSet = {
        dragover: dragHandler,
        drop: dropHandler
    };

    $(".droparea").on(dropHandlerSet);

    fileUploadSuccess(false); // called to ensure that we have initial data
});