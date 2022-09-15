import fastapi
from db_funcs import *  # let the chaos ensue
import datetime
import os

WEBSITE = "http://127.0.0.1:8000"


async def split(iter, num):
    c = 0
    l = []
    for i in iter[::num]:
        l.append(iter[c * num : (c + 1) * num])
    return l


async def make_post(
    id: int, title: str, content: str, date: str, shortened: bool = True
):
    c = await split(content, 340)
    return f"""
<a href="{WEBSITE}/post/{id}" style="text-decoration:none"><div style="background-color:black;
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
        <p style="margin-left: 20px;font-family:sans-serif;font-size:smaller;">Posted on: {date} - ID: {id}</p>
    </div>
    <div style="margin-left:25px;font-size:smaller;">
        <p>{('</p><p>'.join(c[:5])) + (lambda: f'<p style="font-size:medium;color:cadet-blue;font-family:sans-serif;"><a href="{WEBSITE}/post/{id}">Read more...</a></p>' if len(c) > 5 else '')() if shortened else '</p><p>'.join(c)}</p>
    </div>
</div></a>"""


app = fastapi.FastAPI()


@app.middleware("http")
async def evaluate_ip(request, call_next):
    if is_blacklisted(str(request.client.host)):
        raise fastapi.HTTPException(404, "BLACKLISTED CLIENT ADDRESS")
    else:
        return await call_next(request)


@app.get("/new")
async def new():
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


@app.post("/form")
async def form(title: str = fastapi.Form(), content: str = fastapi.Form()):
    if is_inject(title) or is_inject(content):
        raise fastapi.HTTPException(404, "SQL INJECT DETECTED")
    if len(title) > 220:
        return fastapi.HTTPException(413, "TITLE MUST BE UNDER 220 CHARS")
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
async def root():
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
async def posts():
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
    
</head>
<body style="background:#030303;">
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
    for id, title, content, date in get_posts():
        page += await make_post(id, title, content, date)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)


@app.get("/resource/{resource}")
async def fetch_resource(resource: str):
    return fastapi.responses.FileResponse(resource)


@app.get("/post/{post}")
async def post(post: int):
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>tips.saltfleet.org</title>
    
</head>
<body style="background:#030303;">
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
    p = get_post(post)
    page += await make_post(p[0], p[1], p[2], p[3], False)
    page += """    </div></body>
</body>
</html>"""
    return fastapi.responses.HTMLResponse(page)
