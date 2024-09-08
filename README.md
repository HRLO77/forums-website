# website
A forums website, backend written in python, minimal data collection, with efficient and easy to implement features.

To change website address, change the `WEBSITE` constant in `script.js` and `backend.py`.

# requirements
Install requirements with `python -m pip install -r requirements.txt`.

# endpoints
## POST endpoints

* /upvote/

Upvotes a post.

Query params:

post_id - The ID of the post to upvote.

* /downvote/

Downvotes a post.

Query params:

post_id - The ID of the post to downvote.


* /form/
Creates a new post with multipart/form-data data.

Body params:

title - The title of the post.

content - The text of the post.

file - The file to associate with the post.

* /mod_in/

Body params:

password - The password to authenticate moderation

code - the code to execute.

## GET endpoints

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

* /mod/

Returns a form page for moderation purposes.

# Docker

To deploy this, follow the instructions in the Dockerfile within this directory to build and run an image.

# Flows
+
*Flows* are an intuitive, easy and fast way to execute code and send data when events occur. Some purposes may be, a moderation flow to moderate posts, logging flow to log all events that occur on a remote server, and more!


A flows' structure is defined in .yml or .yaml files in `./flows`, it is as presented.


```yaml
FLOW_NAME_HERE: # the name of the flow, should be short and summarize the purpose of it (i.e moderation_flow, pin_flow, statistics)
    event: "*" # valid events are "*" (All of the possible events), "post" (when a post is created) "vote" (when the score of a post changes) and "delete" (when a single or multiple posts are removed)
    file: "FILE_NAME.py" # the name of the script to execute when an event is run (optional)
    address: "http://127.0.0.1:8000" # the address to send the json data to (the same data is given to the file to execute, if provided), this is optional
    threaded: true # a boolean, if true, the file is run on a seperate thread (concurrent), otherwise it is run on the same thread (blocking.), this is optional.
```


If a file is provided and exists in `./flows`, all global and local variables from the database and server process are made available to the script being executed, as well as a variable with the identifier `DATA`, it contains the json data of the event.

* *Note:* All data provided has the type of event being sent as the `"type"` key in the json, values are
`0: "*", 1: "vote", 2: "post", 3: "delete"`

This is true for all data being sent.

# Moderation

You can access the moderation page by going to `URL/mod`. From here, enter the moderation password (the last argument you inputted when running the uvicorn server) and enter the code.

You can copy some quick snippets from underneath to delete a post with ID, pin a post with ID or ban a certain posts author with the ID. `\n` in the code field is replaced with a new line when executed.

It is *highly recommended* you pick a very strong password such as a 64 character alphanumeric string for secuity purposes. Do not share this with anyone that is not a trusted moderator.