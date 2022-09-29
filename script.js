const WEBSITE = "http://127.0.0.1:8000"

let upvote = function (id) { fetch(`${WEBSITE}/upvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let downvote = function (id) { fetch(`${WEBSITE}/downvote`, { method: 'POST', body: JSON.stringify({ "id": id }) }).then(response => response.json()).then(response => { '' }) };

let points = function (id, i) { fetch(`${WEBSITE}/points?post_id=` + id, { method: 'GET' }).then(response => response.json()).then(response => document.getElementById(i).innerHTML = response + ' points') };