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
import os
import aiofiles
import aiohttp
import pathlib
session: aiohttp.ClientSession = aiohttp.ClientSession

SORT_PIN = '&#128392; Pinned by moderators'
WEBSITE = "http://127.0.0.1:8000"


async def split(iter, size: int=470):
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
            <div>
                <img src="{WEBSITE}/resource/user.jpeg" style="height: 2.05%;width:2.05%;border-radius: 50%;margin-left:1.1%;margin-top:1.1%" alt='Anonymous'>
                <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:0.725%;">{title}</p>
                <p style="margin-left: 1.4%;font-family:sans-serif;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" <a style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
                <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↑</button>
                <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↓</button>
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
            <div style="background-color:black;
            text-rendering: optimizeSpeed;
            margin-top:1.5%;
            margin-left:3.3%;
            border-radius: 15px;
            border:0.1%;
            border-style:solid;
            color:white;
            border-color:rgba(95, 158, 160, 0.46);">
                <div>
                    <img src="{WEBSITE}/resource/user.jpeg" style="height: 2.05%;width:2.05%;border-radius: 50%;margin-left:1.1%;margin-top:1.1%" alt='Anonymous'>
                    <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:0.725%;">{title}</p>
                    <p style="margin-left: 1.4%;font-family:sans-serif;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" <a style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
                    <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↑</button>
                    <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');points('{str(id).strip()}', '{rand}');">↓</button>
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
    await start_conn()
    global session
    session = aiohttp.ClientSession()


@app.middleware("http")
async def evaluate_ip(request: fastapi.Request, call_next):
    if await is_blacklisted(str(request.client.host)):
        return fastapi.responses.JSONResponse({"detail", "BLACKLISTED CLIENT ADDRESS"}, 403)
    else:
        return await call_next(request)


@app.post("/upvote")
@limiter.limit("10/minute")
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
@limiter.limit("10/minute")
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

@app.post('/fmd')
@limiter.limit('60/min')
async def fmd(request: fastapi.Request, data: bytes=b'data'):
    pass

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
    <script src='{WEBSITE}/resource/script.js'></script>
    <title>tips.saltfleet.org</title>

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
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:100px;">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
        </div>
    </nav>
    <h1 style='color:white;margin-left:100px;'>New post</h1>
    <form action="{WEBSITE}/form" method="post" enctype="multipart/form-data" id='post_form'>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="title">Title:</label></div>    
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:10%;width:60%;display:flex;"><input type="text" id="title" name="title"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="content">Content:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:10%;width:60%;display:flex;"><input type="text" id="content" name="content"><br><br></div>
        <div style="margin-left: 9.95%;margin-top:2.60416667%;color:white;border-radius:10px"><label for="file">File:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px"><input type="file" id="file" name="file" onchange="uploadFile()"><br><br><progress id='progress' value='0' max='100' style="width: 15.625%;"></progress><p id='status' style="font-size: small'">0% Uploaded</p></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px"><input type="submit" value="Submit"></div>
      </form>
</body>
</html>"""
)


@app.get("/points")
@limiter.limit("60/minute")
async def points(request: fastapi.Request, post_id: str):
    try:
        p = await get_post(post_id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail":"POST NOT FOUND"}, 404)
    else:
        return fastapi.responses.PlainTextResponse(str(len(p[-2]) - len(p[-1])))


@app.post("/form")
@limiter.limit("10/minute")
async def form(
    request: fastapi.Request,
    title: str = fastapi.Form(),
    content: str = fastapi.Form(),
    file: fastapi.UploadFile = fastapi.File(),
):
    if (await is_inject(title)) or (await is_inject(content)):
        return fastapi.responses.JSONResponse({"detail":"SQL INJECT DETECTED"}, 403)
    id: str = ""
    if file.filename != "":
        contents = await file.read()
        async def is_too_big(b: bytes, name):
            '''Checks if a file is more than 1 GiB in size, and is a valid file.'''
            try:
                async with aiofiles.open(name, 'x'):pass
                try:
                    async with aiofiles.open(name, 'wb') as f:await f.write(b)
                except Exception:
                    try:
                        os.remove(name)
                    except Exception:pass
                    return True
                stat = os.stat(name)
                os.remove(name)
                return stat.st_size / (1024 * 1024) > 1024
            except Exception:
                os.remove(name)
                return True

        if (await is_too_big(contents, file.filename)):
            return fastapi.responses.JSONResponse({"detail": "FILE MUST BE UNDER 1 GIGABYTE"}, 413)
        else:
            id = "".join(random.sample(string.ascii_letters, k=52))
            while True:
                if os.path.isfile(f"{id}_{file.filename}"):
                    id = "".join(random.sample(string.ascii_letters, k=52))
                else:
                    break
            if len(await split(f"{id}_{file.filename}")) > 1:return fastapi.responses.JSONResponse({"detail": "FILENAME TOO LARGE"}, 413)
            async with aiofiles.open(f"{id}_{file.filename}", 'x') as f:pass
            async with aiofiles.open(f"{id}_{file.filename}", 'wb') as f:
                await f.write(contents)
    if len(await split(title, 300)) > 1:
        return fastapi.responses.JSONResponse({"detail":"TITLE TOO LARGE"}, 413)
    title = "".join(
        i
        for i in title.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
        if i.isprintable()
    )
    content = "".join(
        i
        for i in content.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
        if i.isprintable()
    )
    if file.filename == "":
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
@limiter.limit("60/minute")
async def root(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{WEBSITE}/resource/dropdown.css">
    <title>tips.saltfleet.org</title>
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
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:100px;">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
        </div>
    </nav>
    <h1 style='margin-left:45%;color:white;'>Root</h1>
</body>
</html>"""
    )


@app.on_event("shutdown")
async def shutdown(*args, **kwargs):
    await close()
    await session.close()


@app.get("/posts")
@limiter.limit("60/minute")
async def posts(request: fastapi.Request, sortby: str='latest'):
    valids = {'latest', 'score', 'length', 'file', 'oldest', 'file_oldest'}
    if not sortby.lower() in valids:return fastapi.responses.JSONResponse({'detail': 'INVALID SORT TYPE', 'sorts': f'{valids}'}, 404)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{WEBSITE}/resource/dropdown.css">
    <title>tips.saltfleet.org</title>
    
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
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:100px;">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
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
    ps = [*await get_posts()]
    pins = []
    c = 0  # save on iterations
    
    for i in ps:
        if i[6] == SORT_PIN:  # 7th index is pin message
            pins += [i]
            ps.pop(c)
        c+=1
    datepost = lambda post: datetime.datetime(int(post[3][:4]), int(post[3][5:7]), int(post[3][8:]))
    if sortby == 'score':
        ps, pins = sorted(ps, key=lambda post: len(post[-2]) - len(post[-1]), reverse=True), sorted(pins, key=lambda post: len(post[-2]) - len(post[-1]), reverse=True)
    elif sortby == 'length':
        ps, pins = sorted(ps, key=lambda post: len(post[2]), reverse=True), sorted(pins, key=lambda post: len(post[2]), reverse=True)
    elif sortby == 'file':
        ps, pins = sorted(ps, key=lambda post: (post[4]!=None, datepost(post)), reverse=True), sorted(pins, key=(lambda post: (post[4]!=None, datepost(post))), reverse=True)
    elif sortby == 'oldest':
        ps, pins = reversed(ps), reversed(pins)
    elif sortby == 'file_oldest':
       ps, pins = reversed(sorted(ps, key=lambda post: (datepost(post), post[4]!=None),)), sorted(sorted(pins, key=(lambda post: (datepost(post), post[4]!=None)),))
    for p in pins:page+=await make_post(*p)
    for p in ps:page+=await make_post(*p)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)


@app.get("/resource/{resource}")
async def fetch_resource(resource: str):
    if resource.strip() in {DATABASE, INJECT, BACKUP} or '/' in resource.strip() or '\\' in resource.strip():
        return fastapi.responses.JSONResponse({"detail": "ACCESS DENIED"}, 403)
    else:
        return fastapi.responses.FileResponse(resource)


@app.get("/post/{post}")
@limiter.limit("60/minute")
async def post(request: fastapi.Request, post: str):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>tips.saltfleet.org</title>
    
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
            <a href="{WEBSITE}/resource/Privacy policy"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:100px;">Policy</button></a>
            <a href="{WEBSITE}/posts"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="color:black;font-size: larger;border-radius:5px;background-color:rgba(98, 0, 255, 0.485);float:right;margin-right:40px;">New post</button></a>
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
