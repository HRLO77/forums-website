const WEBSITE = "http://127.0.0.1:8000"

let _ = function _(el) {
    return document.getElementById(el);
}
  
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
    alert(file.name+ " | " + file.type + ' | ' + Math.round(file.size / 1024) + ' MiB');
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

let upvote = function (id) { fetch(`${WEBSITE}/upvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let downvote = function (id) { fetch(`${WEBSITE}/downvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let points = function (id, i) { fetch(`${WEBSITE}/points?post_id=` + id, { method: 'GET' }).then(response => response.json()).then(response => document.getElementById(i).innerHTML = response + ' points') };

