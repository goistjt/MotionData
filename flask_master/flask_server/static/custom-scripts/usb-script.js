function clicked_upload(id, rec_type) {

    var receivedText = "";

    var input = document.getElementById('uf'+rec_type+'_'+id);

    if (!input){
        alert("System Error. We apologize for the inconvenience.");

    }
    else if (!input.files) {
        alert("This browser doesn't seem to support the `files` property of file inputs.");
    }

    else if (!input.files[0]) {
        alert("Please select a file before clicking 'Load'");
    }

    else {
        var file = input.files[0];
        var fr = new FileReader();
        fr.onload = function(e) {
            var contents = e.target.result;
            send_record_to_add(contents, id);
        };
        fr.readAsText(file);
    }
}

function send_record_to_add(contents, id) {

    var server_endpoint = '/addToSessionFromLocal';

    $.ajax({headers : {},
        type: "POST",
        data: {
            "content" : contents,
            "sess_id" : id
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            if (data.status_code === 701) {
                alert("Upload Functionality Failed: Perhaps Unavailable");
            }
            else if (data.status_code === 200) {
                alert("Update Successful!");
            }
            else {
                alert("Unknown Error - Update Not Successful");
            }
        }});
}

function clicked_create_session(id, rec_type) {

    var receivedText = "";

    var input = document.getElementById('create_session_file');

    if (!input){
        alert("System Error. We apologize for the inconvenience.");
    }

    else if (!input.files) {
        alert("This browser doesn't seem to support the `files` property of file inputs.");
    }

    else if (!input.files[0]) {
        alert("Please select a file before clicking 'Load'");
    }

    else {
        var file = input.files[0];
        var fr = new FileReader();
        fr.onload = function(e) {
            var contents = e.target.result;
            send_session_to_create(contents);
        };
        fr.readAsText(file);
    }
}

function send_session_to_create(contents) {

    var server_endpoint = '/createSessionFromLocal';

    $.ajax({headers : {},
        type: "POST",
        data: {
            "content" : contents
        },
        dataType: "json",
        url: server_endpoint,
        success: function (data) {
            if (data.status_code === 701) {
                alert("Upload Functionality Failed: Perhaps Unavailable");
            }

            else if (data.status_code === 200) {
                alert("Update Successful!");
            }

            else {
                alert("Unknown Error - Update Not Successful");
            }
        }});
}

function clicked_update_android_files(){
    // Function to send call to endpoint that updates Android cache
    var server_endpoint = '/updateAndroidCache';

    $.ajax({headers : {},
        url: server_endpoint,
        success: function (data) {
            if (data.status_code === 503) {
                alert("Update Functionality Failed: Perhaps Unavailable");
            }
            else if (data.status_code === 200) {
                alert("Update Successful!");
            }
            else {
                alert("Unknown Error: Update Not Successful");
            }
        }});
}

function clicked_clear_cache(){
    // Function to send call to endpoint that updates Android cache
    var server_endpoint = '/clearAndroidCache';

    $.ajax({headers : {},
        url: server_endpoint,
        success: function (data) {
            if (data.status_code === 500) {
                alert("Error Clearing Cache: Not Successful");
            }
            else if (data.status_code === 200) {
                alert("Android Cache Clearing Successful!");
            }
            else {
                alert("Unknown Error: Clearing Not Successful");
            }
        }});
}