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
import aiofiles
import aiohttp
import gzip
from aiofiles import os
import tracemalloc
import subprocess
<<<<<<< HEAD
import sys
from typing import Optional

SORT_PIN = '&#128392; Pinned'
WEBSITE = "http://localhost:8000"
# WEBSITE = os.environ['DETA_SPACE_APP_HOSTNAME']


async def split(iter, size: int=500):
=======


SORT_PIN = '&#128392; Pinned'
WEBSITE = "http://127.0.0.1:8000"


async def split(iter, size: int=470):
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
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
        if cur <= size:
            s += char
        else:
            l.append(s)
            s = ""
            cur = 0
    l.append(s)
    return l


async def make_post(
    id: str,
    title: str,
    content: str,
    date: str,
    file: str,
    ip: str,
    pin: str=None,
    upvotes: set[str]=set(),
    downvotes: set[str]=set(),
    shortened: bool = True,
):
    rand = "".join(random.sample(string.ascii_letters, k=52))
    c: list[str] = await split(content) # type: ignore
    if pin is None:
        return f"""
    <div>
        <div style="background-color:black;
        text-rendering: optimizeSpeed;
        margin-top:1.5%;
        margin-left:3.3%;
        border-radius: 15px;
        border:0.1%;
        border-style:solid;
        color:white;
        border-color:rgba(95, 158, 160, 0.46);">
<<<<<<< HEAD
            <script src='{WEBSITE}/resource/script.js'></script>
=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
            <div>
                <img src="{WEBSITE}/resource/user.jpeg" style="height: 2.05%;width:2.05%;border-radius: 50%;margin-left:1.1%;margin-top:1.1%" alt='Anonymous'>
                <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:0.725%;">{title}</p>
                <p style="margin-left: 1.4%;font-family:sans-serif;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" <a style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
<<<<<<< HEAD
                <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');sleep(1000);points('{str(id).strip()}', '{rand}');">↑</button>
                <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');sleep(1000);points('{str(id).strip()}', '{rand}');">↓</button>
=======
                <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↑</button>
                <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↓</button>
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
                <p style="font-family:sans-serif;font-size:medium;display:inline-block;vertical-align:top;margin-left:0.7%" id="{rand}">{len(upvotes)-len(downvotes)} points</p>
            </div>
            <div style="margin-left:1.75%;font-size:smaller;">
                <p>{('</p><p>'.join(c[:5])) + (lambda: f'<p><a href="{WEBSITE}/post/{id}" style="text-decoration:none;font-size:medium;font-family:sans-serif;color:cadetblue">Read more...</a></p>' if len(c) > 5 else (lambda: f'<br><br><p style="font-family:sans-serif">Attachment:<br> <a href="{WEBSITE}/resource/{file}">{file[53:]}</a></p>' if file is not None else '')())() if shortened else '</p><p>'.join(c) + (lambda: f'<br><br><p style="font-family:sans-serif">Attachment:<br> <a href="{WEBSITE}/resource/{file}">{file[53:]}</a></p>' if file is not None else '')()}</p>
            </div>
        </div>
    </div>
    """
    else:
        return f"""
    <div>
        <p style="text-rendering: optimizeSpeed;color:white;font-family:'Courier New', Courier, monospace;font-size:large;margin-left:3.3%;margin-top:1.5%">	
            {pin}</p>
        <div>
<<<<<<< HEAD
            
=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
            <div style="background-color:black;
            text-rendering: optimizeSpeed;
            margin-top:1.5%;
            margin-left:3.3%;
            border-radius: 15px;
            border:0.1%;
            border-style:solid;
            color:white;
            border-color:rgba(95, 158, 160, 0.46);">
<<<<<<< HEAD
                <script src='{WEBSITE}/resource/script.js'></script>
=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
                <div>
                    <img src="{WEBSITE}/resource/user.jpeg" style="height: 2.05%;width:2.05%;border-radius: 50%;margin-left:1.1%;margin-top:1.1%" alt='Anonymous'>
                    <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:0.725%;">{title}</p>
                    <p style="margin-left: 1.4%;font-family:sans-serif;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" <a style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
<<<<<<< HEAD
                    <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');sleep(1000);points('{str(id).strip()}', '{rand}');">↑</button>
                    <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');sleep(1000);points('{str(id).strip()}', '{rand}');">↓</button>
=======
                    <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↑</button>
                    <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↓</button>
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
                    <p style="font-family:sans-serif;font-size:medium;display:inline-block;vertical-align:top;margin-left:0.7%" id="{rand}">{len(upvotes)-len(downvotes)} points</p>
                </div>
                <div style="margin-left:1.75%;font-size:smaller;">
                    <p>{('</p><p>'.join(c[:5])) + (lambda: f'<p><a href="{WEBSITE}/post/{id}" style="text-decoration:none;font-size:medium;font-family:sans-serif;color:cadetblue">Read more...</a></p>' if len(c) > 5 else (lambda: f'<br><br><p style="font-family:sans-serif">Attachment:<br> <a href="{WEBSITE}/resource/{file}">{file[53:]}</a></p>' if file is not None else '')())() if shortened else '</p><p>'.join(c) + (lambda: f'<br><br><p style="font-family:sans-serif">Attachment:<br> <a href="{WEBSITE}/resource/{file}">{file[53:]}</a></p>' if file is not None else '')()}</p>
                </div>
            </div>
        </div>
    """


limiter = slowapi.Limiter(key_func=util.get_remote_address)
app = fastapi.FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
async def start(*args, **kwargs):
    global session
    tracemalloc.start()
    await start_conn()
    session = aiohttp.ClientSession()
    try:await asyncio.to_thread(subprocess.run, ['python', 'flow_loader.py'])
<<<<<<< HEAD
    except Exception as e:print(f'Error loading flows in backend: {e}')
=======
    except Exception:pass
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
    await asyncio.to_thread(load_flows)


@app.middleware("http")
async def evaluate_ip(request: fastapi.Request, call_next):
    if await is_blacklisted(str(request.client.host)):
        return fastapi.responses.JSONResponse({"detail", "BLACKLISTED CLIENT ADDRESS"}, 403)
    else:
        return await call_next(request)


@app.post("/upvote")
<<<<<<< HEAD
@limiter.limit("5/minute")
=======
@limiter.limit("10/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def upvote(request: fastapi.Request, id: bytes = fastapi.Body()):
    try:
        id: str = json.loads(id.decode())["id"]
        post = await get_post(id)
        if (
            str(request.client.host) in (post[-1])
            and str(request.client.host) in post[-2]
        ):  # both
            await remove_downvote(str(request.client.host), id)
            await remove_upvote(str(request.client.host), id)
        elif (str(request.client.host) in post[-1]) and not (
            str(request.client.host) in post[-2]
        ):  # 1 downvote no upvote
            await add_upvote(str(request.client.host), id)
            await remove_downvote(str(request.client.host), id)
        elif not str(request.client.host) in post[-1] and (
            str(request.client.host) in post[-2]
        ):  # no downvote and 1 upvote
            await remove_upvote(str(request.client.host), id)
        elif not (str(request.client.host) in post[-1]) and not (
            str(request.client.host) in post[-2]
        ):  # no downvote and no upvote
            await add_upvote(str(request.client.host), id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail": f"{e}"}, 500)


@app.post("/downvote")
<<<<<<< HEAD
@limiter.limit("5/minute")
=======
@limiter.limit("10/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def downvote(request: fastapi.Request, id: bytes = fastapi.Body()):
    try:
        id: str = json.loads(id.decode())["id"]
        post = await get_post(id)
        if (str(request.client.host) in post[-1]) and str(request.client.host) in post[
            -2
        ]:  # both
            await remove_downvote(str(request.client.host), id)
            await remove_upvote(str(request.client.host), id)
        elif (
            str(request.client.host) in post[-1]
            and not str(request.client.host) in post[-2]
        ):  # downvote no upvote
            await remove_downvote(str(request.client.host), id)
        elif not (str(request.client.host) in post[-1]) and (
            str(request.client.host) in post[-2]
        ):  # no downvote and 1 upvote
            await add_downvote(str(request.client.host), id)
            await remove_upvote(str(request.client.host), id)
        elif not (str(request.client.host) in post[-1]) and not (
            str(request.client.host) in post[-2]
        ):  # no downvote and no upvote
            await add_downvote(str(request.client.host), id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail": f"{e}"}, 500)

<<<<<<< HEAD

@app.get('/raw')
@limiter.limit('20/minute')
=======
@app.post('/fmd')
@limiter.limit('10/min')
async def fmd(request: fastapi.Request, data: fastapi.UploadFile=fastapi.File()):
    pass

@app.get('/raw')
@limiter.limit('60/min')
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def raw(request: fastapi.Request):
    posts = await get_posts()
    return fastapi.responses.JSONResponse({i[0]: [*i[1:5], *i[6:-2], len(i[-2])-len(i[-1])] for i in posts})

@app.get("/new")
<<<<<<< HEAD
@limiter.limit("20/minute")
=======
@limiter.limit("60/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def new(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src='{WEBSITE}/resource/script.js'></script>
<<<<<<< HEAD
    <title>tips.massey.org</title>
    <style>
    #progressWrapper {{
        display: none;
        width: 270px; /* Matches the width of the text boxes */
        background-color: #f3f3f3;
        border: 1px solid #ccc;
        margin-top: 20px;
        border-radius: 5px; /* Optional: Rounds the edges */
    }}

    #progressBar {{
        width: 270px;
        height: 20px;
        background-color: #4caf50;
        border-radius: 5px; /* Optional: Rounds the edges */
    }}
    </style>
=======
    <title>tips.saltfleet.org</title>

>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
</head>
<body style="background:#030303;">
    
    <nav style="
    display:flex;
    justify-content: center;
    align-items:center;
    height: 40pt;
    background-color:rgba(95, 158, 160, 0.46);;
    font-family: 'Montserrat', sans-serif;
    ">
        <div>
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:-17.5%">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;display:inline-flexbox">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;margin-bottom:1%">New post</button></a>
        </div>
    </nav>
<<<<<<< HEAD
    <h1 style='color:white;margin-left:7.35%;'>New post</h1>
    <form id="post_form">
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="title">Title:</label></div>    
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:30%;width:100%;display:flex;"><input type="text" id="title" name="title"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="content">Content:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:30%;width:100%;display:flex;"><input type="text" id="content" name="content"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="file">File:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px">
            <input type="file" id="file" name="file"><br><br>
            <div id="progressWrapper">
                <div id="progressBar"></div>
            </div>
        </div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px">
            <button type="button" onclick="submitForm()">Submit</button>
        </div>
    </form>
</body>
</html>
"""
=======
    <h1 style='color:white;margin-left:100px;'>New post</h1>
    <form action="{WEBSITE}/form" method="post" enctype="multipart/form-data" id='post_form'>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="title">Title:</label></div>    
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:30%;width:90%;display:flex;"><input type="text" id="title" name="title"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="content">Content:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:30%;width:90%;display:flex;"><input type="text" id="content" name="content"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="file">File:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px"><input type="file" id="file" name="file" onchange="uploadFile()"><br><br><progress id='progress' value='0' max='100' style="width: 15.625%;"></progress><p id='status' style="font-size: small'">0% Uploaded</p></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px"><input type="submit" value="Submit"></div>
      </form>
</body>
</html>"""
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
)


@app.get("/points")
<<<<<<< HEAD
@limiter.limit("20/minute")
=======
@limiter.limit("60/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def points(request: fastapi.Request, post_id: str):
    try:
        p = await get_post(post_id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail":"POST NOT FOUND"}, 404)
    else:
        return fastapi.responses.PlainTextResponse(str(len(p[-2]) - len(p[-1])))


@app.post("/form")
<<<<<<< HEAD
@limiter.limit("1/minute")
=======
@limiter.limit("10/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def form(
    request: fastapi.Request,
    title: str = fastapi.Form(),
    content: str = fastapi.Form(),
<<<<<<< HEAD
    file: Optional[fastapi.UploadFile] = fastapi.File(None),
=======
    file: fastapi.UploadFile = fastapi.File(),
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
):
    global session
    if (await is_inject(title)) or (await is_inject(content)):
        return fastapi.responses.JSONResponse({"detail":"SQL INJECT DETECTED"}, 403)
    id: str = ""
<<<<<<< HEAD
    if not(file is None):
        contents = await file.read()
        async def is_too_big(b: bytes, name):
            '''Checks if a file is more than 3 MiB in size after gzip compression, and is a valid file.'''
            size = 3146000 # 3 mbs
            try:
                try:

                    async with aiofiles.open(name, 'wb') as f:await f.write(b)
                    size = (await os.stat(name)).st_size  # / (1024 * 1024)
                except Exception as e:
                    fastapi.responses.JSONResponse({f"detail": f"ERROR IN UPLOADING FILE: {e}"}, 500)
=======
    if file.filename != "":
        contents = await file.read()
        async def is_too_big(b: bytes, name):
            '''Checks if a file is more than 2 GiB in size after gzip compression, and is a valid file.'''
            size = 1024*2+1
            try:
                async with aiofiles.open(name, 'x'):pass
                try:

                    async with aiofiles.open(name, 'wb') as f:await f.write(b)
                    size = (await os.stat(name)).st_size / (1024 * 1024)
                except Exception:
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
                    try:await os.remove(name)
                    except Exception:pass
                    return True, size
                try:
<<<<<<< HEAD
                    if size > 3146000:await os.remove(name)
                except Exception:pass 
                return size > 3146000, size
=======
                    if size > 1024*2:await os.remove(name)
                except Exception:pass
                return size > 1024*2, size
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
            except Exception:
                await os.remove(name)
                
                return True, size
        try:contents=await asyncio.to_thread(gzip.compress, contents)
        except Exception:pass
        res = await is_too_big(contents, file.filename)
        if (res[0]):
<<<<<<< HEAD
            return fastapi.responses.JSONResponse({"detail": f"FILE MUST BE UNDER 3 MiB AFTER COMPRESSION, FILE WAS {res[1]//1049000}.{res[1]%1049000} MiB"}, 413)
        else:
            id = "".join(random.sample(string.ascii_letters, k=52))
            # while True:
            #     if await os.path.isfile(f"{id}_{file.filename}"):
            #         id = "".join(random.sample(string.ascii_letters, k=52))
            #     else:
            #         break
=======
            return fastapi.responses.JSONResponse({"detail": f"FILE MUST BE UNDER 2 GIGABYTES AFTER COMPRESSION, FILE WAS {res[1]//1024}.{res[1]%1024} GiB"}, 413)
        else:
            id = "".join(random.sample(string.ascii_letters, k=52))
            while True:
                if await os.path.isfile(f"{id}_{file.filename}"):
                    id = "".join(random.sample(string.ascii_letters, k=52))
                else:
                    break
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
            if len(await split(f"{id}_{file.filename}")) > 1:return fastapi.responses.JSONResponse({"detail": "FILENAME TOO LARGE"}, 413)
            await os.rename(file.filename, f"{id}_{file.filename}")
    if len(await split(title, 300)) > 1:
        return fastapi.responses.JSONResponse({"detail":"TITLE TOO LARGE"}, 413)
    title = "".join(
        i
        for i in title.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
<<<<<<< HEAD
        .replace('&', '&amp;')
        .replace('-', '&ndash;')
=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
        if i.isprintable()
    )
    content = "".join(
        i
        for i in content.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
<<<<<<< HEAD
        .replace('&', '&amp;')
        .replace('-', '&ndash;')
        if i.isprintable()
    )
    if file is None:
=======
        if i.isprintable()
    )
    if file.filename == "":
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
        returned = await new_post(
            title, content, datetime.datetime.utcnow(), str(request.client.host)
        )
    else:
        returned = await new_post(
            title,
            content,
            datetime.datetime.utcnow(),
            str(request.client.host),
            f"{id}_{file.filename}",
        )
    async with session.get(f'{WEBSITE}/post/{returned[0]}') as resp:
        return fastapi.responses.HTMLResponse(await resp.text())


@app.get("/")
<<<<<<< HEAD
@limiter.limit("20/minute")
=======
@limiter.limit("60/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def root(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{WEBSITE}/resource/dropdown.css">
<<<<<<< HEAD
    <title>tips.massey.org</title>
=======
    <title>tips.saltfleet.org</title>
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
</head>
<body style="background:#030303;">
    <nav style="
    display:flex;
    justify-content: center;
    align-items:center;
    height: 40pt;
    background-color:rgba(95, 158, 160, 0.46);
    font-family: 'Montserrat', sans-serif;
    ">
        <div>
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:-17.5%">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;display:inline-flexbox">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;margin-bottom:1%">New post</button></a>
        </div>
    </nav>
    <h1 style='margin-left:45%;color:white;'>Root</h1>
</body>
</html>"""
    )


@app.on_event("shutdown")
async def shutdown(*args, **kwargs):
    global session
    await close()
    await session.close()
<<<<<<< HEAD
    exit()


@app.get("/posts")
@limiter.limit("20/minute")
=======


@app.get("/posts")
@limiter.limit("60/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def posts(request: fastapi.Request, sortby: str='latest', pgn: int=0):
    valids = {'latest', 'score', 'length', 'file', 'oldest', 'file_oldest'}
    if not sortby.lower() in valids:return fastapi.responses.JSONResponse({'detail': 'INVALID SORT TYPE', 'sorts': f'{valids}'}, 404)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{WEBSITE}/resource/dropdown.css">
<<<<<<< HEAD
    <title>tips.massey.org</title>
=======
    <title>tips.saltfleet.org</title>
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
    
</head>
<body style="background:#030303;">
    <script src='{WEBSITE}/resource/script.js'></script>
    <div style="background: #030303">
        <nav style="
        display:flex;
        justify-content: center;
        align-items:center;
        height: 40pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;
        ">
            <div>
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:-17.5%">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;display:inline-flexbox">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;margin-bottom:1%">New post</button></a>
            </div>
        </nav>
    <div class="dropdown">
        <button onclick="drop()" class="dropbtn">Sort by:</button>
        <div id="myDropdown" class="dropdown-content">
            <a href="{WEBSITE}/posts?sortby=latest">Latest</a>
            <a href="{WEBSITE}/posts?sortby=oldest">Oldest</a>
            <a href="{WEBSITE}/posts?sortby=score">Score</a>
            <a href="{WEBSITE}/posts?sortby=length">Length</a>
            <a href="{WEBSITE}/posts?sortby=file">File</a>
            <a href="{WEBSITE}/posts?sortby=file_oldest">File Oldest</a>
        </div>
    </div>
""" 
    # really fast, efficient splicing of posts for each page!
<<<<<<< HEAD
    LEN = 11
=======
    LEN = 25
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
    ps = [*await get_posts()]
    if LEN*pgn > len(ps):
        return fastapi.responses.JSONResponse({'detail': f'UNKOWN PAGE NUMBER {pgn}'}, 404)
    pins = []
    c = 0  # save on iterations
    
    d=0
    for i in ps:
        if i[6] == SORT_PIN:  # 7th index is pin message
            pins += [i]
            d+=1
            ps.pop(c)
        c+=1
    t=LEN-d
    del d
    datepost = lambda post: datetime.datetime(int(post[3][:4]), int(post[3][5:7]), int(post[3][8:]))
    if sortby == 'score':
        ps, pins = sorted(ps, key=lambda post: len(post[-2]) - len(post[-1]), reverse=True), sorted(pins, key=lambda post: len(post[-2]) - len(post[-1]), reverse=True)
    elif sortby == 'length':
        ps, pins = sorted(ps, key=lambda post: len(post[2]), reverse=True), sorted(pins, key=lambda post: len(post[2]), reverse=True)
    elif sortby == 'file':
        ps, pins = sorted(ps, key=lambda post: (post[4]!=None, datepost(post)), reverse=True), sorted(pins, key=(lambda post: (post[4]!=None, datepost(post))), reverse=True)
    elif sortby == 'oldest':
<<<<<<< HEAD
        ps, pins = [*reversed(ps)], [*reversed(pins)]
    elif sortby == 'file_oldest':
       ps, pins = [*reversed(sorted(ps, key=lambda post: (datepost(post), post[4]!=None),))], [*sorted(sorted(pins, key=(lambda post: (datepost(post), post[4]!=None)),))]
    ps = ps[t*pgn:t*pgn+t]
=======
        ps, pins = reversed(ps), reversed(pins)
    elif sortby == 'file_oldest':
       ps, pins = reversed(sorted(ps, key=lambda post: (datepost(post), post[4]!=None),)), sorted(sorted(pins, key=(lambda post: (datepost(post), post[4]!=None)),))
    ps = ([*ps])[t*pgn:t*pgn+t]
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
    del t

    for p in pins:page+=await make_post(*p)
    for p in ps:page+=await make_post(*p)
    page += f"""
    <br><br><br><br>
    <a href="{WEBSITE}/posts?sortby={sortby}&pgn={pgn-1}"><button style="color:white;float:left;margin-left:45%;font-size:larger;border-color:cadetblue;background-color:#030303;border-radius:15%;width:2.2%;height:3%;display:flexbox;">&lt;</button></a>
    <a href="{WEBSITE}/posts?sortby={sortby}&pgn={pgn+1}"><button style="color:white;float:right;margin-right:49%;font-size:larger;border-color:cadetblue;background-color:#030303;border-radius:15%;width:2.2%;height:3%;display:flexbox;">&gt;</button></a>
    </div>
</body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)


@app.get("/resource/{resource}")
async def fetch_resource(resource: str):
    if resource.strip() in {DATABASE, INJECT, BACKUP} or '/' in resource.strip() or '\\' in resource.strip():
        return fastapi.responses.JSONResponse({"detail": "ACCESS DENIED"}, 403)
    else:
        async def stream(file: str):
            async with aiofiles.open(file, 'rb') as rb:
                contents = await rb.read()
                try:contents = await asyncio.to_thread(gzip.decompress, contents)
                except Exception:pass
                yield contents
        return fastapi.responses.StreamingResponse(stream(resource))


@app.get("/post/{post}")
<<<<<<< HEAD
@limiter.limit("20/minute")
=======
@limiter.limit("60/minute")
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
async def post(request: fastapi.Request, post: str):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
<<<<<<< HEAD
    <title>tips.massey.org</title>
=======
    <title>tips.saltfleet.org</title>
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
    
</head>
<body style="background:#030303;">
    <link rel="stylesheet" href="{WEBSITE}/resource/dropdown.css">
    <script src='{WEBSITE}/resource/script.js'></script>
    <div style="background: #030303">
        <nav style="
        display:flex;
        justify-content: center;
        align-items:center;
        height:40pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;
        ">
            <div>
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:-17.5%">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;display:inline-flexbox">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;margin-bottom:1%">New post</button></a>
            </div>
        </nav>
    <div class="dropdown">
        <button onclick="drop()" class="dropbtn">Sort by:</button>
        <div id="myDropdown" class="dropdown-content">
            <a href="{WEBSITE}/posts?sortby=latest">Latest</a>
            <a href="{WEBSITE}/posts?sortby=oldest">Oldest</a>
            <a href="{WEBSITE}/posts?sortby=score">Score</a>
            <a href="{WEBSITE}/posts?sortby=length">Length</a>
            <a href="{WEBSITE}/posts?sortby=file">File</a>
            <a href="{WEBSITE}/posts?sortby=file_latest">File latest</a>
        </div>
    </div>"""
    try:
        p: tuple[str, str, str, str, str, str, str, set[str], set[str]] = await get_post(post)
    except Exception:
        return fastapi.responses.JSONResponse({"detail", "POST NOT FOUND"}, 404)
    page += await make_post(*p, False)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)
<<<<<<< HEAD


@app.get('/mod')
@limiter.limit('10/minute')
async def moderate(request: fastapi.Request,):
    return fastapi.responses.HTMLResponse(f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src='{WEBSITE}/resource/script.js'></script>
    <title>tips.massey.org</title>
</head>
<body style="background:#030303;">
    
    <nav style="
    display:flex;
    justify-content: center;
    align-items:center;
    height: 40pt;
    background-color:rgba(95, 158, 160, 0.46);;
    font-family: 'Montserrat', sans-serif;
    ">
        <div>
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:-17.5%">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;display:inline-flexbox">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(74, 142, 182, 0.485);float:none;margin-left:5%;margin-bottom:1%">New post</button></a>
        </div>
    </nav>
    <h1 style='color:white;margin-left:7.35%;'>New post</h1>
    <form id="mod_form">
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="password">Password:</label></div>    
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:30%;width:100%;display:flex;"><input type="text" id="password" name="password"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="code">Code:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:30%;width:100%;display:flex;"><input type="text" id="code" name="code"><br><br></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px">
            <button type="button" onclick="moderate()">Moderate</button>
        </div>
    </form>
    <p style='color:white;margin-left:7.35%;'>async def main():\\n  print(await delete_post('',))\\nasyncio.run(main())</p>
    <br>
    <p style='color:white;margin-left:7.35%;'>async def main():\\n  print(await rep_post('',pin="{SORT_PIN.replace('&', '&amp;')}"))\\nasyncio.run(main())</p>
    <br>
    <p style='color:white;margin-left:7.35%;'>async def main():\\n  print(await ban_author('',))\\nasyncio.run(main())</p>
    <br>
</body>
</html>
""")
    
@app.post('/mod_in')
@limiter.limit('10/minute')
async def moderate(request: fastapi.Request, password: str = fastapi.Form(), code: str = fastapi.Form()):
    if password != sys.argv[-1]:
        return fastapi.responses.JSONResponse({'detail': 'INCORRECT PASSWORD'}, 401)
    name = f'{"".join(random.sample(string.ascii_letters, k=5))}.txt'
    async with aiofiles.open(name, 'x') as f:
        pass
    code = f'import sys;\nsys.stdout=open("{name}", "w");\n{code}\nsys.stdout.close()\n'.replace('\\n', '\n') # inject some logging code
    await asyncio.gather(asyncio.to_thread(exec, code, globals(), locals()))
    async with aiofiles.open(name, 'r') as f:
        code = fastapi.responses.HTMLResponse(await f.read())
    await os.remove(name)
    return code
=======
>>>>>>> cd751be441c9cc833a6b65d5d5dd39bc512ed0bc
