# website
A website to post anonymous tips (about school because I dunno how to do english)
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
Returns an HTML page to submit a form that creates a new post.

# Docker
To deploy this, follow the instructions in the Dockerfile within this directory to build and run an image.