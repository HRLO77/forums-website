import fastapi
import fastapi.params
from db_funcs import *  # let the chaos ensue
import datetime
import slowapi
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi import util
import string
import json
import random
import gzip
from aiofiles import os
import tracemalloc
import subprocess
import sys
from typing import Optional

SORT_PIN = '&#128392; Pinned'
WEBSITE = ""


# WEBSITE = os.environ['DETA_SPACE_APP_HOSTNAME']

SWEARS = {'sl*t', 'sh*t', 'f*ck', 'p*ss', 'd*mn', 'slvt', 'p*ss*', 'f*g', 'fag', 'r*t*rd', 'r*trd', 'tism', 't*sm', 'c*nt', 'cvnt', 'b*st*rd', 'b*tch', 'w*tch', 'b*th', 'f*ckr', 'f*ck*r', 'n*g', 'n*gga', '*gga', 'n*gg', 's*x', 'p*rn', 'prn', 'j*w', 'v*g', 'v*g*n', 'v*g*', 'c*c', 'd*c', 'p*n*s', 'r*d*n', 'r*dn', 't*t', 'b**b', 'g*n', 'n33r','n3gr', 'ngr', 'c*m', 'wh*r', 'wh*r*', 'n***r', 'n**r', 'n****r', 'n*gg*r', 'n*g*r', 'n*gl*t', 'n*grl*t', 'n*gr*', 'n*g*o', 'n*g*'}x = {'a': '*', 'e': '*', 'i': '*', 'o': '*', 'u': '*', 'y': '*'}
x.update({i: '*' for i in ((string.punctuation+string.digits).replace(' ', ''))})
table = str.maketrans(x)

async def basic_check(s: str):
    s = s.lower().replace('ing ', ' ').replace('s ', ' ').replace('ed ', ' ').translate(table)
    for i in s.split():
        if i in SWEARS:
            return True
    return False

def get_client_ip_blocking(request: fastapi.Request):
    'returns the client api based on either proxy or host'
    client_ip = request.headers.get('X-Forwarded-For')
    
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host
    return client_ip

async def get_client_ip(request: fastapi.Request):
    'returns the client api based on either proxy or host'
    client_ip = request.headers.get('X-Forwarded-For')
    
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host
    return client_ip

async def split(iter, size: int=600):
    
    special = {
        "@",
        "#",
        "%",
        "&",
        "$",
    }
    large = {"k", "m", "n", "b", "c", "x", "z", "d", "s", "a", "o", "e", " ", "g"}
    small = {i for i in string.printable.lower() if i not in large or not i in special}
    l = []
    cur = 0
    s = ""
    for char in iter:
        cur += (
            int(char.lower() in large) * 1.5
            + int(char.lower() in small) * 1.5
            + int(char.lower() in special) * 0.5
        )
        if cur <= size:
            s += char
        else:
            
            l.append(s)
            s = char
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
    shortened: bool = True
):
    rand = "".join(random.sample(string.ascii_letters+string.digits, k=LENGTH_OF_ID))
    if file is not None:
        filename = file[len(STORE_DIR):]
    c: tuple[str] = (" ".join(content.split()[:233]), ) if shortened else (content, )
    if pin is None:
        return f"""
    <div>
        <div style="background-color:black;
        margin-top:1.5%;
        margin-left:3.3%;
        border-radius: 15px;
        border:0.1%;
        border-style:solid;
        color:white;
        border-color:rgba(95, 158, 160, 0.46);">
            <script src='{WEBSITE}/resource/?resource=script.js'></script>
            <div>
                <img src="{WEBSITE}/resource/?resource=user.jpeg" style="height: 2.05%;width:2.05%;border-radius: 50%;margin-left:1.1%;margin-top:1.1%" alt='Anonymous'>
                <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:0.725%;">{title}</p>
                <p style="margin-left: 1.4%;font-family:sans-serif;text-rendering:optimizeSpeed;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
                <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');sleep(500);points('{str(id).strip()}', '{rand}');">↑</button>
                <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');sleep(500);points('{str(id).strip()}', '{rand}');">↓</button>
                <p style="font-family:sans-serif;text-rendering:optimizeSpeed;font-size:medium;display:inline-block;vertical-align:top;margin-left:0.7%" id="{rand}">{len(upvotes)-len(downvotes)} points</p>
            </div>
            <div style="margin-left:1.75%;margin-right:1.75%;font-size:medium;font-family:sans-serif;text-rendering:optimizeSpeed;text-rendering:optimizeSpeed;line-height:200%;">
                <p>{('</p><p>'.join(c)) + '</p>' + (lambda: f'<p><a href="{WEBSITE}/post/{id}" style="text-decoration:none;font-size:medium;font-family:sans-serif;text-rendering:optimizeSpeed;color:cadetblue">Read more...</a></p>' if (len(content.split())>233) else (lambda: f'<hr><p style="font-family:sans-serif;text-rendering:optimizeSpeed">Attachment: <a href="{WEBSITE}/resource/?resource={file}">{filename[LENGTH_OF_ID+1:]}</a></p>' if file is not None else '')())() if shortened else '</p><p>'.join(c) + '</p>' + (lambda: f'<hr><p style="font-family:sans-serif;text-rendering:optimizeSpeed">Attachment: <a href="{WEBSITE}/resource/?resource={file}">{filename[LENGTH_OF_ID+1:]}</a></p>' if file is not None else '')()}
            </div>
        </div>
    </div>
    """
    else:
        return f"""
    <div>
        <p style="color:white;font-family:'Courier New', Courier, monospace;font-size:large;margin-left:3.3%;margin-top:1.5%">	
            {pin}</p>
        <div>
            <div style="background-color:black;
            margin-top:1.5%;
            margin-left:3.3%;
            border-radius: 15px;
            border:0.1%;
            border-style:solid;
            color:white;
            border-color:rgba(95, 158, 160, 0.46);">
                <script src='{WEBSITE}/resource/?resource=script.js'></script>
                <div>
                    <img src="{WEBSITE}/resource/?resource=user.jpeg" style="height: 2.05%;width:2.05%;border-radius: 50%;margin-left:1.1%;margin-top:1.1%" alt='Anonymous'>
                    <p style="font-size:larger;display:inline-block;vertical-align:top;margin-left:0.725%;">{title}</p>
                    <p style="margin-left: 1.4%;font-family:sans-serif;text-rendering:optimizeSpeed;font-size:medium;">Posted on: {date} - <a href="{WEBSITE}/post/{id}" style="text-decoration:none;color:cadetblue">ID: {id}</a></p>
                    <button style="margin-left:1.4%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="upvote('{str(id).strip()}');sleep(500);points('{str(id).strip()}', '{rand}');">↑</button>
                    <button style="margin-left:1.37%;color:white;background-color:#030303;border-radius:50%;border-color:cadetblue;margin-top:1.05%" onclick="downvote('{str(id).strip()}');sleep(500);points('{str(id).strip()}', '{rand}');">↓</button>
                    <p style="font-family:sans-serif;text-rendering:optimizeSpeed;font-size:medium;display:inline-block;vertical-align:top;margin-left:0.7%" id="{rand}">{len(upvotes)-len(downvotes)} points</p>
                </div>
            <div style="margin-left:1.75%;margin-right:1.75%;font-size:medium;font-family:sans-serif;text-rendering:optimizeSpeed;text-rendering:optimizeSpeed;line-height:200%;">
                <p>{('</p><p>'.join(c)) + '</p>' + (lambda: f'<p><a href="{WEBSITE}/post/{id}" style="text-decoration:none;font-size:medium;font-family:sans-serif;text-rendering:optimizeSpeed;color:cadetblue">Read more...</a></p>' if (len(content.split())>233) else (lambda: f'<hr><p style="font-family:sans-serif;text-rendering:optimizeSpeed">Attachment: <a href="{WEBSITE}/resource/?resource={file}">{filename[LENGTH_OF_ID+1:]}</a></p>' if file is not None else '')())() if shortened else '</p><p>'.join(c) + '</p>' + (lambda: f'<hr><p style="font-family:sans-serif;text-rendering:optimizeSpeed">Attachment: <a href="{WEBSITE}/resource/?resource={file}">{filename[LENGTH_OF_ID+1:]}</a></p>' if file is not None else '')()}
            </div>
            </div>
        </div>
    </div>
    """

limiter = slowapi.Limiter(key_func=get_client_ip_blocking)#util.get_remote_address
app = fastapi.FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)




@app.on_event("startup")
async def start(*args, **kwargs):
    tracemalloc.start()
    try:
        await setup_dbs(True)
        try:await asyncio.to_thread(subprocess.run, ['python', 'flow_loader.py'])
        except Exception as e:print(f'Error loading flows in backend: {e}')
        await asyncio.to_thread(load_flows)
    except Exception as e:
        print('Error on start up:', e, '. \n\n Attempting to restart all dbs...')
        await setup_dbs()
    if (await os.path.isdir('/app_data')):
        print(await os.listdir('/app_data'))

@app.middleware("http")
async def evaluate_ip(request: fastapi.Request, call_next):
    ip = await get_client_ip(request)
    if await is_blacklisted(str(ip)):
        return fastapi.responses.JSONResponse({"detail": "BLACKLISTED CLIENT ADDRESS"}, 403)
    else:
        return await call_next(request)


@app.post("/upvote")
@limiter.limit("5/minute")
async def upvote(request: fastapi.Request, id: bytes = fastapi.Body()):
    ip = await get_client_ip(request)
    try:
        id: str = json.loads(id.decode())["id"]
        post = await get_post(id)
        if (
            str(ip) in (post[-1])
            and str(ip) in post[-2]
        ):  # both
            await remove_downvote(str(ip), id)
            await remove_upvote(str(ip), id)
        elif (str(ip) in post[-1]) and not (
            str(ip) in post[-2]
        ):  # 1 downvote no upvote
            await add_upvote(str(ip), id)
            await remove_downvote(str(ip), id)
        elif not str(ip) in post[-1] and (
            str(ip) in post[-2]
        ):  # no downvote and 1 upvote
            await remove_upvote(str(ip), id)
        elif not (str(ip) in post[-1]) and not (
            str(ip) in post[-2]
        ):  # no downvote and no upvote
            await add_upvote(str(ip), id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail": f"{e}"}, 500)

# @app.get('/redirect')
# @limiter.limit('10/minute')
# async def 

@app.post("/downvote")
@limiter.limit("5/minute")
async def downvote(request: fastapi.Request, id: bytes = fastapi.Body()):
    ip = await get_client_ip(request)
    try:
        id: str = json.loads(id.decode())["id"]
        post = await get_post(id)
        if (str(ip) in post[-1]) and str(ip) in post[
            -2
        ]:  # both
            await remove_downvote(str(ip), id)
            await remove_upvote(str(ip), id)
        elif (
            str(ip) in post[-1]
            and not str(ip) in post[-2]
        ):  # downvote no upvote
            await remove_downvote(str(ip), id)
        elif not (str(ip) in post[-1]) and (
            str(ip) in post[-2]
        ):  # no downvote and 1 upvote
            await add_downvote(str(ip), id)
            await remove_upvote(str(ip), id)
        elif not (str(ip) in post[-1]) and not (
            str(ip) in post[-2]
        ):  # no downvote and no upvote
            await add_downvote(str(ip), id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail": f"{e}"}, 500)


@app.get('/raw')
@limiter.limit('1/minute')
async def raw(request: fastapi.Request):
    posts = await get_posts()
    return fastapi.responses.JSONResponse({i[0]: [*i[1:5], *i[6:-2], len(i[-2])-len(i[-1])] for i in posts})

@app.get("/new")
@limiter.limit("20/minute")
async def new(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src='{WEBSITE}/resource/?resource=script.js'></script>
    <title>Massey Tips</title>
    <link rel="icon" href="{WEBSITE}/resource/?resource=favicon.ico" />

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
</head>
<body style="background:#030303;">
    
        <nav style="
        display:flex;
        justify-content:space-evenly;
        align-items:center;
        height: 100pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;text-rendering:optimizeSpeed;flex-direction:row;
        ">
            <a href="{WEBSITE}/resource/?resource=Privacy_policy.txt"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">Policy</button>
            </a>
            <a href="{WEBSITE}/posts"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">New post</button></a>
        </nav>
    <h1 style='color:white;margin-left:20%;font-size:largest'>New post</h1>
    <form id="post_form">
        <div style="margin-left: 22.5%;margin-top:2.60416667%;color:white;border-radius:10px;font-size:large"><label for="title">Title:</label></div>    
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;display:flexbox;"><input type="text" id="title" name="title" style="height:30px;width:60%;font-size:large"><br><br></div>
        <div style="margin-left: 22%;margin-top:2.60416667%;color:white;border-radius:10px;font-size:large;display:flexbox;"><label for="content">Content:</label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:50%;width:100%;display:flexbox;"><input type="text" id="content" name="content" style="height:30px;width:90%;font-size:medium"><br><br></div>
        <div style="margin-left: 23%;margin-top:2.60416667%;color:white;border-radius:10px;font-size:large;"><label for="file">File:</label></div>
        <div style="margin-left: 21.5%;margin-top:2.60416667%;color:white;border-radius:10px">
            <input type="file" id="file" name="file" style="font-size:medium;"><br><br>
            <div id="progressWrapper" style="margin-left:-5.75%">
                <div id="progressBar"></div>
            </div>
        </div>
        <div style="margin-left: 22.2%;margin-top:2.60416667%;color:white;border-radius:10px">
            <button type="button" onclick="submitForm()" style="font-size: large;">Submit</button>
        </div>
    </form>
</body>
</html>

"""
)


@app.get("/points")
@limiter.limit("20/minute")
async def points(request: fastapi.Request, post_id: str):
    try:
        p = await get_post(post_id)
    except Exception as e:
        return fastapi.responses.JSONResponse({"detail":"POST NOT FOUND"}, 404)
    else:
        return fastapi.responses.PlainTextResponse(str(len(p[-2]) - len(p[-1])))


@app.post("/form")
@limiter.limit("1/minute")
async def form(
    request: fastapi.Request,
    pin: str = None,
    title: str = fastapi.Form(),
    content: str = fastapi.Form(),
    file: Optional[fastapi.UploadFile] = fastapi.File(None),
):
    ip = await get_client_ip(request)
    if (await is_inject(title)) or (await is_inject(content)):
        return fastapi.responses.JSONResponse({"detail":"SQL INJECT DETECTED"}, 403)
    id: str = ""
    if (await basic_check(content)):
        return fastapi.responses.JSONResponse({"detail":"INAPPROPRIATE MATERIAL DETECTED"}, 422)
    elif ((await basic_check(title))):
        return fastapi.responses.JSONResponse({"detail":"INAPPROPRIATE MATERIAL DETECTED"}, 422)
    title = title.replace('   ', '').replace('  ', ' ')  # remove extra white spaces
    content = content.replace('   ', '').replace('  ', ' ')
    if not(file is None):
        contents = await file.read()
        async def is_too_big(b: bytes, name):
            '''Checks if a file is more than 5 MiB in size after gzip compression, and is a valid file.'''
            size = 6245000
            try:
                try:

                    async with aiofiles.open(name, 'wb') as f:await f.write(b)
                    size = (await os.stat(name)).st_size  # / (1024 * 1024)
                except Exception as e:
                    fastapi.responses.JSONResponse({f"detail": f"ERROR IN UPLOADING FILE: {e}"}, 500)
                    try:await os.remove(name)
                    except Exception:pass
                    return True, size
                try:
                    if size > 5245000:await os.remove(name)
                except Exception:pass 
                return size > 5245000, size
            except Exception:
                await os.remove(name)
                
                return True, size
        try:contents=await asyncio.to_thread(gzip.compress, contents)
        except Exception:pass
        res = await is_too_big(contents, file.filename)
        if (res[0]):
            return fastapi.responses.JSONResponse({"detail": f"FILE MUST BE UNDER 5 MiB AFTER COMPRESSION, FILE WAS {res[1]//1049000}.{res[1]%1049000} MiB"}, 413)
        else:
            id = "".join(random.sample(string.ascii_letters+string.digits, k=LENGTH_OF_ID))
            # while True:
            #     if await os.path.isfile(f"{id}_{file.filename}"):
            #         id = "".join(random.sample(string.ascii_letters+string.digits, k=LENGTH_OF_ID))
            #     else:
            #         break
            if len(await split(f"{id}_{file.filename}")) > 1:return fastapi.responses.JSONResponse({"detail": "FILENAME TOO LARGE"}, 413)
            await os_copy(file.filename, f"{STORE_DIR}{id}_{file.filename}")
    if len(await split(title, 300)) > 1:
        return fastapi.responses.JSONResponse({"detail":"TITLE TOO LARGE"}, 413)
    if len(await split(content)) > 15:
        return fastapi.responses.JSONResponse({"detail":"CONTENT TOO LARGE"}, 413)
    title = "".join(
        i
        for i in title.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
        .replace('&', '&amp;')
        .replace('-', '&ndash;')
        if i.isprintable()
    )
    content = "".join(
        i
        for i in content.replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
        .replace('&', '&amp;')
        .replace('-', '&ndash;')
        if i.isprintable()
    )
    if file is None:
        returned = await new_post(
            title, content, datetime.datetime.now(datetime.UTC), str(ip), pin=(SORT_PIN if pin==sys.argv[-1] else None)
        )
    else:
        returned = await new_post(
            title,
            content,
            datetime.datetime.now(datetime.UTC),
            str(ip),
            f"{STORE_DIR}{id}_{file.filename}", pin=(SORT_PIN if pin==sys.argv[-1] else None)
        )


@app.get("/")
@limiter.limit("20/minute")
async def root(request: fastapi.Request):
    return fastapi.responses.HTMLResponse(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{WEBSITE}/resource/?resource=dropdown.css">
    <title>Massey Tips</title>
    <link rel="icon" href="{WEBSITE}/resource/?resource=favicon.ico" />

</head>
<body style="background:#030303;">
        <nav style="
        display:flex;
        justify-content:space-evenly;
        align-items:center;
        height: 100pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;text-rendering:optimizeSpeed;flex-direction:row;
        ">
            <a href="{WEBSITE}/resource/?resource=Privacy_policy.txt"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">Policy</button>
            </a>
            <a href="{WEBSITE}/posts"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">New post</button></a>
        </nav>
    <h1 style='margin-left:47.2%;color:white;'>Root</h1>
</body>
</html>"""
    )


@app.on_event("shutdown")
async def shutdown(*args, **kwargs):
    try:
        print('Backing up...')
        await update_inject()
        print('Closing...')
        await close()
    except Exception as e:
        print('Error on close: ', e)


@app.get("/posts")
@limiter.limit("20/minute")
async def posts(request: fastapi.Request, sortby: str='latest', pgn: int=0):
    valids = {'latest', 'score', 'length', 'file', 'oldest', 'file_oldest'}
    if not sortby.lower() in valids:return fastapi.responses.JSONResponse({'detail': 'INVALID SORT TYPE', 'sorts': f'{valids}'}, 404)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{WEBSITE}/resource/?resource=dropdown.css">
    <title>Massey Tips</title>
    <link rel="icon" href="{WEBSITE}/resource/?resource=favicon.ico" />

    
</head>
<body style="background:#030303;">
    <script src='{WEBSITE}/resource/?resource=script.js'></script>
    <div style="background: #030303">
        <nav style="
        display:flex;
        justify-content:space-evenly;
        align-items:center;
        height: 100pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;text-rendering:optimizeSpeed;flex-direction:row;
        ">
            <a href="{WEBSITE}/resource/?resource=Privacy_policy.txt"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">Policy</button>
            </a>
            <a href="{WEBSITE}/posts"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">New post</button></a>
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
    LEN = 11
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
        ps, pins = [*reversed(ps)], [*reversed(pins)]
    elif sortby == 'file_oldest':
       ps, pins = [*reversed(sorted(ps, key=lambda post: (datepost(post), post[4]!=None),))], [*sorted(sorted(pins, key=(lambda post: (datepost(post), post[4]!=None)),))]
    ps = ps[t*pgn:t*pgn+t]
    del t

    for p in pins:page+=await make_post(*p)
    for p in ps:page+=await make_post(*p)
    page += f"""
    <br><br><br><br>
        <div style="flex-direction:row;justify-content:space-evenly;align-items:center;display:flex;">
            <a href="https://massey-tips.fly.dev/posts?sortby=latest&pgn=-1"><button style="color:white;font-size:xx-large;border-color:cadetblue;background-color:#030303;border-radius:15%">&lt;</button></a>
            <a href="https://massey-tips.fly.dev/posts?sortby=latest&pgn=1"><button style="color:white;font-size:xx-large;border-color:cadetblue;background-color:#030303;border-radius:15%">&gt;</button></a>
        </div>
</body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)


@app.get("/resource/")
@limiter.limit('20/minute')
async def fetch_resource(request: fastapi.Request, resource: str):
    if resource.strip() in {DATABASE, INJECT, BACKUP}:
        return fastapi.responses.JSONResponse({"detail": "ACCESS DENIED"}, 403)
    
    match = re.match(f'^{STORE_DIR}([a-zA-Z0-9]{{{LENGTH_OF_ID}}})_', resource)
    if match is None:
        if '/' in resource.strip() or '\\' in resource.strip() or DATABASE in resource.strip() or INJECT in resource.strip() or BACKUP in resource.strip():
            return fastapi.responses.JSONResponse({"detail": "ACCESS DENIED"}, 403)
    
    async def stream(file: str):
        async with aiofiles.open(file, 'rb') as rb:
            contents = await rb.read()
            try:contents = await asyncio.to_thread(gzip.decompress, contents)
            except Exception:pass
            yield contents
    return fastapi.responses.StreamingResponse(stream(resource))


@app.get("/post/{post}")
@limiter.limit("20/minute")
async def post(request: fastapi.Request, post: str):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <title>Massey Tips</title>
    <link rel="icon" href="{WEBSITE}/resource/?resource=favicon.ico" />

    
</head>
<body style="background:#030303;">
    <link rel="stylesheet" href="{WEBSITE}/resource/?resource=dropdown.css">
    <script src='{WEBSITE}/resource/?resource=script.js'></script>
    <div style="background: #030303">
        <nav style="
        display:flex;
        justify-content:space-evenly;
        align-items:center;
        height: 100pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;text-rendering:optimizeSpeed;flex-direction:row;
        ">
            <a href="{WEBSITE}/resource/?resource=Privacy_policy.txt"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">Policy</button>
            </a>
            <a href="{WEBSITE}/posts"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">New post</button></a>
        </nav>
"""
    try:
        p: tuple[str, str, str, str, str, str, str, set[str], set[str]] = await get_post(post)
    except Exception:
        return fastapi.responses.JSONResponse({"detail", "POST NOT FOUND"}, 404)
    page += await make_post(*p, False)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)


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
    <script src='{WEBSITE}/resource/?resource=script.js'></script>
    <title>Massey Tips</title>
    <link rel="icon" href="{WEBSITE}/resource/?resource=favicon.ico" />

</head>
<body style="background:#030303;">
    
        <nav style="
        display:flex;
        justify-content:space-evenly;
        align-items:center;
        height: 100pt;
        background-color:rgba(95, 158, 160, 0.46);
        font-family: 'Montserrat', sans-serif;text-rendering:optimizeSpeed;flex-direction:row;
        ">
            <a href="{WEBSITE}/resource/?resource=Privacy_policy.txt"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">Policy</button>
            </a>
            <a href="{WEBSITE}/posts"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">All posts</button></a>
            <a href="{WEBSITE}/new"><button style="cursor: pointer; color: black; font-size: larger; border-radius: 5px; background-color: rgba(74, 142, 182, 0.485); height: 50px; width: 100px;">New post</button></a>
        </nav>
    <h1 style='color:white;margin-left:19%;font-size:largest'>Moderation page</h1>
    <form id="mod_form">
        <div style="margin-left: 23%;margin-top:2.60416667%;color:white;border-radius:10px;font-size:large"><label for="password">Password: </label></div>    
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;display:flexbox;"><input type="text" id="password" name="password" style="height:30px;width:60%;font-size:large"><br><br></div>
        <div style="margin-left: 24%;margin-top:2.60416667%;color:white;border-radius:10px;font-size:large;display:flexbox;"><label for="code">Code: </label></div>
        <div style="margin-left: 6.5%;margin-top:2.60416667%;color:white;border-radius:10px;height:50%;width:100%;display:flexbox;"><input type="text" id="code" name="code" style="height:30px;width:90%;font-size:medium"><br><br></div>
        <div style="margin-left: 23%;margin-top:2.60416667%;color:white;border-radius:10px">
            <button type="button" onclick="moderate()" style="font-size: large;">Moderate</button>
        </div>
    </form>
    <p style='color:white;margin-left:7.35%;font-size:large'>async def main():\\n  print(await delete_post("",))\\nasyncio.run(main())</p>
    <br>
    <p style='color:white;margin-left:7.35%;font-size:large'>async def main():\\n  print(await rep_post("",pin="{SORT_PIN.replace('&', '&amp;')}"))\\nasyncio.run(main())</p>
    <br>
    <p style='color:white;margin-left:7.35%;font-size:large'>async def main():\\n  print(await ban_author("",))\\nasyncio.run(main())</p>
    <br>
    <p style='color:white;margin-left:7.35%;font-size:large'>async def main():\\n async for i in delete_posts(["", ""]):pass\\nasyncio.run(main())</p>
</body>
</html>
""")
    
@app.post('/mod_in')
@limiter.limit('10/minute')
async def moderate(request: fastapi.Request, password: str = fastapi.Form(), code: str = fastapi.Form()):
    if (password.strip()) != sys.argv[-1]:
        return fastapi.responses.JSONResponse({'detail': 'INCORRECT PASSWORD'}, 401)
    name = f'{"".join(random.sample(string.ascii_letters+string.digits, k=LENGTH_OF_ID))}.txt'
    code = f'{code}'.replace('\\n', '\n')
    await update_inject()
    try:
        await asyncio.gather(asyncio.to_thread(exec, code, globals(), locals()))
    except Exception as e:
        return fastapi.responses.JSONResponse({'detail': f'ERROR EXECUTING COMMAND: {e}'}, 500)
    
