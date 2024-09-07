<<<<<<< HEAD
const WEBSITE = "http://localhost:8000"
// const WEBSITE = process.env.DETA_SPACE_APP_HOSTNAME
=======
const WEBSITE = "http://127.0.0.1:8000"
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc

let _ = function _(el) {
    return document.getElementById(el);
}
  
<<<<<<< HEAD
=======
let progressHandler = function progressHandler(event) {
var percent = (event.loaded / event.total) * 100;
    _("progress").value = Math.round(percent);
    if (percent != 100){_("status").innerHTML = Math.round(percent) + "% uploaded";}
    else{_("status").innerHTML = 'Successfully uploaded.'}
}

let completeHandler = function completeHandler(event) {
    _("status").innerHTML = 'Successfully uploaded.';
    _("progress").value = 100; //wil clear progress bar after successful upload
}

let errorHandler = function errorHandler(event) {
    _("status").innerHTML = "Upload Failed";
}

let abortHandler = function abortHandler(event) {
    ("status").innerHTML = "Upload Cancelled";
}

let uploadFile = function uploadFile() {
    var file = _("file").files[0];
    var size = Math.round(file.size / 1024 / 1000);
    var t = ' MiB';
    if (size > 999){
      t = ' GiB';
      size = (size+'').slice(-3) + '.' + (size+'').slice(-3, 0)
    }
    alert(file.name+ " | " + file.type + ' | ' + size + t);
    var formdata = new FormData();
    formdata.append("data", file);
    var ajax = new XMLHttpRequest();
    ajax.upload.addEventListener("progress", progressHandler, false);
    ajax.addEventListener("load", completeHandler, false);
    ajax.addEventListener("error", errorHandler, false);
    ajax.addEventListener("abort", abortHandler, false);
    ajax.open('POST', `${WEBSITE}/fmd`);
    ajax.send(formdata);
}

>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
function drop() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  // Close the dropdown menu if the user clicks outside of it
  window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }

<<<<<<< HEAD
function submitForm() {
    // Get form data
    const formData = new FormData();
    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;
    const fileInput = document.getElementById('file');
    formData.append('title', title);
    formData.append('content', content);
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    } 
    // Validate form fields if necessary
    if (!title || !content) {
        alert("Please fill in all fields");
        return;
    }

    // Create a FormData object to hold the form data
    

    

    // Show the progress bar
    document.getElementById('progressWrapper').style.display = 'block';

    // Create an AJAX request to submit the form
    const xhr = new XMLHttpRequest();
    
    // Monitor progress event
    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable) {
            const percentage = (e.loaded / e.total) * 100;
            document.getElementById('progressBar').style.width = percentage + '%';
        }
    });

    // Request finished successfully
    xhr.onload = function() {
        if (xhr.status === 200) {
            alert("Form uploaded successfully!");
            // Reset progress bar and form
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressWrapper').style.display = 'none';
            document.getElementById('post_form').reset();
        } else {
            alert("Error uploading form.");
        }
    };

    // Send data to server (replace '{WEBSITE}/form' with your server script)
    xhr.open('POST', `${WEBSITE}/form`, true);
    xhr.send(formData);
}

=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
let upvote = function (id) { fetch(`${WEBSITE}/upvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let downvote = function (id) { fetch(`${WEBSITE}/downvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let points = function (id, i) { fetch(`${WEBSITE}/points?post_id=` + id, { method: 'GET' }).then(response => response.json()).then(response => document.getElementById(i).innerHTML = response + ' points') };
<<<<<<< HEAD

function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
      if ((new Date().getTime() - start) > milliseconds){
        break;
      }
    }
  }

function moderate() {
    // Get form data
    const title = document.getElementById('password').value;
    const content = document.getElementById('code').value;

    // Validate form fields if necessary
    if (!title || !content) {
        alert("Please fill in all fields");
        return;
    }

    // Create a FormData object to hold the form data
    const formData = new FormData();
    formData.append('password', title);
    formData.append('code', content);

    const xhr = new XMLHttpRequest();
    
    // Monitor progress event


    // Request finished successfully
    xhr.onload = function() {
        if (xhr.status === 200) {
            alert("Command executed successfully!");
            // Reset progress bar and form
            document.getElementById('mod_form').reset();
        } else {
            alert("Error executing command.");
        }
    };

    // Send data to server (replace '{WEBSITE}/form' with your server script)
    xhr.open('POST', `${WEBSITE}/mod_in`, true);
    xhr.send(formData);
}
=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
