# website
A website to post anonymous tips (about school because I dunno how to pass english).

To change website address, change the `WEBSITE` constant in `script.js` and `backend.py`.
## Managing posts
To manage posts in the database (pinning posts, removing authors, banning IP's).

Write code desired in interact.py and run `python interact.py --user`.

An example is in interact.py to pin a post with an ID. Pinned posts will be sorted by the
`SORT_PIN` variable in `backend.py`, which is currently equal to `'&#128392; Pinned'`.
# requirements
Install requirements with `python -m pip install -r requirements.txt`.

# endpoints
## POST endpoints
All POST endpoints are ratelimited to 10/minute.

* /upvote/
Upvotes a post.
Query params:
post_id - The ID of the post to upvote.

* /downvote/

Downvotes a post.

Query params:

post_id - The ID of the post to downvote.

* /fmd/

Recieves only multipart/formdata for files (progress loading in JS) for progress bars.

Body params:

data - bytes.

* /form/
Creates a new post with multipart/form-data data.

Body params:

title - The title of the post.

content - The text of the post.

file - The file to associate with the post.

## GET endpoints
All GET endpoints are ratelimited to 60/minute.

* /raw/

Returns all of the posts in the database in JSON format

* /posts/

Returns HTML page with all the posts.

Query params:

sortby - What order posts should be sorted in.

* /post/
Views a single post.

Query params:

post - The ID of the post to view.

* /resource/
Returns a file from the server.

Path params:

resource - The path of the file to return.

* /
The root of the website.

* /points/
Returns the points of a post.

Query params:

post_id - Returns the points of this post ID.

* /new/

Returns an HTML page to submit a form.

# Docker

To deploy this, follow the instructions in the Dockerfile within this directory to build and run an image.

# Flows

*Flows* are an intuitive, easy and fast way to execute code and send data when events occur. Some purposes may be, a moderation flow to moderate posts, logging flow to log all events that occur on a remote server, and more!


A flows' structure is defined in .yml or .yaml files in `./flows`, it is as presented.


```yaml
FLOW_NAME_HERE: # the name of the flow, should be short and summarize the purpose of it (i.e moderation_flow, pin_flow, statistics)
    event: "*" # valid events are "*" (All of the possible events), "post" (when a post is created) "vote" (when the score of a post changes) and "delete" (when a single or multiple posts are removed, this excludes author purges or bans)
    file: "FILE_NAME.py" # the name of the script to execute when an event is run (optional)
    address: "http://127.0.0.1:8001" # the address to send the json data to (the same data is given to the file to execute, if provided), this is optional
    threaded: true # a boolean, if true, the file is run on a seperate thread (concurrent), otherwise it is run on the same thread (blocking.), this is optional.
```


If a file is provided and exists in `./flows`, all global and local variables from the database and server process are made available to the script being executed, as well as a variable with the identifier `DATA`, it contains the json data of the event.

* *Note:* All data provided has the type of event being sent as the `"type"` key in the json, values are
`0: "*", 1: "vote", 2: "post", 3: "delete"`

This is true for all data being sent.

An example of a flow script, code, and test server are in `./flows/example.yaml`, `./flows/bot.py`, and `./test_server.py`.

Start the test server by running the command `python -m uvicorn test_server:app --port 8001 --reload`.
