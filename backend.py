import fastapi
from db_funcs import *  # let the chaos ensue
import datetime
import slowapi
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi import util
import string
import json
import random

WEBSITE = "http://127.0.0.1:8000"


async def split(iter):
    largest = {
        "@",
        "#",
        "%",
        "&",
        "$",
    }
    large = {"k", "m", "n", "b", "c", "x", "z", "d", "s", "a", "o", "e", " ", "g"}
    small = {i for i in string.printable if i not in large or not i in largest}
    l = []
    cur = 0
    s = ""
    for char in iter:
        cur += (
            int(char.lower() in large) * 2
            + int(char.lower() in small) * 1.5
            + int(char.lower() in largest) * 2.5
        )
        if cur <= 430:
            s += char
        else:
            l.append(s)
            s = ""
            cur = 0
    l.append(s)
    return l


async def make_post(
    id: int,
    title: str,
    content: str,
    date: str,
    upvotes: set[str],
    downvotes: set[str],
    shortened: bool = True,
):
    rand = ''.join(random.sample(string.ascii_letters, k=52))
    c = await split(content)
    return f"""
<div style="background-color:black;
text-rendering: optimizeSpeed;
margin:50px;
border-radius: 15px;
border:5px;
border-style:solid;
color:white;
border-color:rgba(95, 158, 160, 0.46);">
    <div>
        <img src="{WEBSITE}/resource/user.jpeg" style="height: 30px;width:30px;border-radius: 512px;margin-left:15px;margin-top:15px;">
        <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:10px">{title}</p>
        <p style="margin-left: 20px;font-family:sans-serif;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
            <button style="margin-left:20px;color:white;background-color:#030303;border-radius:18px;border-color:cadetblue;margin-top:15px" onclick="upvote({str(id).strip()});points({str(id).strip()}, '{rand}');">↑</button>
            <button style="margin-left:20px;color:white;background-color:#030303;border-radius:18px;border-color:cadetblue;margin-top:15px" onclick="downvote({str(id).strip()});points({str(id).strip()}, '{rand}');">↓</button>
            <p style="font-family:sans-serif;font-size:medium;display:inline-block;vertical-align:top;margin-left:10px" id="{rand}">{len(upvotes)-len(downvotes)} points</p>
    </div>
    <div style="margin-left:25px;font-size:smaller;">
        <p>{('</p><p>'.join(c[:5])) + (lambda: f'<p><a href="{WEBSITE}/post/{id}" style="text-decoration:none;font-size:medium;font-family:sans-serif;color:cadetblue">Read more...</a></p>' if len(c) > 5 else '')() if shortened else '</p><p>'.join(c)}</p>
    </div>
</div>"""


limiter = slowapi.Limiter(key_func=util.get_remote_address)
app = fastapi.FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def evaluate_ip(request: fastapi.Request, call_next):
    if is_blacklisted(str(request.client.host)):
        raise fastapi.HTTPException(403, "BLACKLISTED CLIENT ADDRESS")
    else:
        return await call_next(request)


@app.post("/upvote")
@limiter.limit("10/minute")
async def upvote(request: fastapi.Request, id: bytes=fastapi.Body()):
    try:
        id = json.loads(id.decode())["id"]
        if (str(request.client.host) in get_post(id)[-1]) and str(
            request.client.host
        ) in get_post(id)[
            -2
        ]:  # both
            remove_downvote(str(request.client.host), id)
            remove_upvote(str(request.client.host), id)
        elif (str(request.client.host) in get_post(id)[-1]) and not (
            str(request.client.host) in get_post(id)[-2]
        ):  # downvote no upvote
            raise fastapi.HTTPException(409, {"detail": "CLIENT HAS DOWNVOTED"})
        elif not (str(request.client.host) in get_post(id)[-1]) and (
            str(request.client.host) in get_post(id)[-2]
        ):  # no downvote and 1 upvote
            remove_upvote(str(request.client.host), id)
        elif not (str(request.client.host) in get_post(id)[-1]) and not (
            str(request.client.host) in get_post(id)[-2]
        ):  # no downvote and no upvote
            add_upvote(str(request.client.host), id)
    except Exception as e:
        raise fastapi.exceptions.HTTPException(500, e)


@app.post("/downvote")
@limiter.limit("10/minute")
async def downvote(request: fastapi.Request, id: bytes = fastapi.Body()):
    try:
        id = json.loads(id.decode())["id"]
        if (str(request.client.host) in get_post(id)[-1]) and str(
            request.client.host
        ) in get_post(id)[
            -2
        ]:  # both
            remove_downvote(str(request.client.host), id)
            remove_upvote(str(request.client.host), id)
        elif (str(request.client.host) in get_post(id)[-1]) and not (
            str(request.client.host) in get_post(id)[-2]
        ):  # downvote no upvote
            remove_downvote(str(request.client.host), id)
        elif not (str(request.client.host) in get_post(id)[-1]) and (
            str(request.client.host) in get_post(id)[-2]
        ):  # no downvote and 1 upvote
            raise fastapi.HTTPException(409, {"detail": "CLIENT HAS UPVOTED"})
        elif not (str(request.client.host) in get_post(id)[-1]) and not (
            str(request.client.host) in get_post(id)[-2]
        ):  # no downvote and no upvote
            add_downvote(str(request.client.host), id)
    except Exception as e:
        raise fastapi.exceptions.HTTPException(500, e)


@app.get("/new")
@limiter.limit("60/minute")
async def new(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
    
</head>
<body style="background:#030303;">
    <nav style="
    display:flex;
    justify-content: center;
    align-items:center;
    height: 6vh;
    background-color:rgba(95, 158, 160, 0.46);;
    font-family: 'Montserrat', sans-serif;
    ">
        <div>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:80px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
        </div>
    </nav>
    <h1 style='color:white;margin-left:100px;'>New post</h1>
    <form action="{WEBSITE}/form" method="post">
        <div style="margin-left: 150px;margin-top:50px;color:white;border-radius:10px"><label for="title">Title:</label></div>    
        <div style="margin-left: 100px;margin-top:50px;color:white;border-radius:10px"><input type="text" id="title" name="title"><br><br></div>
        <div style="margin-left: 150px;margin-top:50px;color:white;border-radius:10px"><label for="content">Content:</label></div>
        <div style="margin-left: 100px;margin-top:50px;color:white;border-radius:10px"><input type="text" id="content" name="content"><br><br></div>
        <div style="margin-left: 100px;margin-top:50px;color:white;border-radius:10px"><input type="submit" value="Submit"></div>
      </form>
</body>
</html>"""
)

@app.get('/points')
@limiter.limit('60/minute')
async def points(request: fastapi.Request, post_id: int):
    try:
        p = get_post(post_id)
    except Exception:
        raise fastapi.HTTPException(404, "POST NOT FOUND")
    else:
        return fastapi.responses.PlainTextResponse(str(len(p[4])-len(p[5])))

@app.post("/form")
@limiter.limit("10/minute")
async def form(
    request: fastapi.Request, title: str = fastapi.Form(), content: str = fastapi.Form()
):
    if is_inject(title) or is_inject(content):
        raise fastapi.HTTPException(403, "SQL INJECT DETECTED")
    if len(title) > 220:
        raise fastapi.HTTPException(413, "TITLE MUST BE UNDER 220 CHARS")
    title = "".join(i for i in title.replace('<', '&lt;').replace('>', '&gt;').replace("'", '&#39;').replace('"', '&quot;') if i.isprintable())
    content = "".join(i for i in content.replace('<', '&lt;').replace('>', '&gt;').replace("'", '&#39;').replace('"', '&quot;') if i.isprintable())
    returned = new_post(title, content, datetime.datetime.utcnow())
    return fastapi.responses.HTMLResponse(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
</head>
<body style="background:#030303;">
    <div style="background: #030303">
    <p style='color: white;margin-left:150px;margin-top:150px;'>Submitted! Check your post <a href='{WEBSITE}/post/{returned[0]}'>here</a>!</p>
    </div>
</body>
</html>"""
    )


@app.get("/")
@limiter.limit("60/minute")
async def root(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
</head>
<body style="background:#030303;">
    <nav style="
    display:flex;
    justify-content: center;
    align-items:center;
    height: 6vh;
    background-color:rgba(95, 158, 160, 0.46);;
    font-family: 'Montserrat', sans-serif;
    ">
        <div>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:80px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
        </div>
    </nav>
    <h1 style='margin-left:95vh;color:white;'>Root</h1>
</body>
</html>"""
    )


@app.on_event("shutdown")
async def shutdown():
    close()


@app.get("/posts")
@limiter.limit("60/minute")
async def posts(request: fastapi.Request):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
    
</head>
<body style="background:#030303;">
    <script src='{WEBSITE}/resource/script.js'></script>
    <div style="background: #030303">
        <nav style="
        display:flex;
        justify-content: center;
        align-items:center;
        height: 6vh;
        background-color:rgba(95, 158, 160, 0.46);;
        font-family: 'Montserrat', sans-serif;
        ">
            <div>
                <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:80px;">All posts</button></a>
                <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
            
            </div>
        </nav>"""
    for args in get_posts():
        page += await make_post(*args)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)


@app.get("/resource/{resource}")
async def fetch_resource(resource: str):
    return fastapi.responses.FileResponse(resource)


@app.get("/post/{post}")
@limiter.limit("60/minute")
async def post(request: fastapi.Request, post: int):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
    
</head>
<body style="background:#030303;">
    <script src='{WEBSITE}/resource/script.js'></script>
    <div style="background: #030303">
        <nav style="
        display:flex;
        justify-content: center;
        align-items:center;
        height: 6vh;
        background-color:rgba(95, 158, 160, 0.46);;
        font-family: 'Montserrat', sans-serif;
        ">
            <div>
                <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:80px;">All posts</button></a>
                <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
            </div>
        </nav>"""
    try:
        p: tuple[int, str, str, str, set[str], set[str]] = get_post(post)
    except Exception:
        raise fastapi.HTTPException(404, {"detail": "POST NOT FOUND"})
    page += await make_post(*p, False)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)
