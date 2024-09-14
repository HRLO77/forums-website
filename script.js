WEBSITE = "";//
// const WEBSITE = process.env.DETA_SPACE_APP_HOSTNAME
  
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
            alert(`Error uploading form ${xhr.status}: ${xhr.response}`);
        }
    };

    // Send data to server (replace '{WEBSITE}/form' with your server script)
    xhr.open('POST', `${WEBSITE}/form`, true);
    xhr.send(formData);
}

let upvote = function (id) { fetch(`${WEBSITE}/upvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let downvote = function (id) { fetch(`${WEBSITE}/downvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let points = function (id, i) { fetch(`${WEBSITE}/points?post_id=` + id, { method: 'GET' }).then(response => response.json()).then(response => document.getElementById(i).innerHTML = response + ' points') };

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
            
            alert(`Error executing command ${xhr.status}: ${xhr.response}`);
        }
    };

    // Send data to server (replace '{WEBSITE}/form' with your server script)
    xhr.open('POST', `${WEBSITE}/mod_in`, true);
    xhr.send(formData);
}
