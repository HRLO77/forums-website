from aiofiles import os
import aiofiles
import glob
import asyncio
import typing
import datetime
import random
import ast
import string
import aiosqlite
import re
import pickle
import aiohttp
import json
import sys

sys.path.append(__import__('os').getcwd())
DATABASE = "database.sqlite3"
BACKUP = "backup.sqlite3"
INJECT = "inject.sqlite3"
FLOWS = {}
cursor: aiosqlite.Connection = aiosqlite.connect(DATABASE)
session: aiohttp.ClientSession | None = None

LENGTH_OF_ID = 5

async def handler(data: dict | list | tuple, t: int, clean: bool=False):
    '''Handles flow data you dont want to: {'*': 0, 'vote': 1, 'post': 2, 'delete': 3}'''
    global session
    async with aiomysql.connect() as f:
        f.c
    types = {'*': 0, 'vote': 1, 'post': 2, 'delete': 3}
    for (flow, dat) in FLOWS.items():
        
        if types[dat['event'].lower()] == t or types[dat['event'].lower()] == 0:
            
            if isinstance(data, dict):
                if clean:data: dict = {id: [*second[1:5], *second[6:-2], len(second[-2])-len(second[-1])] for id, second in data.items()}
            else:
                if clean:data: dict = {data[0]: [*data[1:5], *data[6:-2], len(data[-2])-len(data[-1])]}
            data.update({'type': t})
            
            try:
                file = dat['file']
                threaded = dat['threaded']
                assert isinstance(threaded, bool)
                assert (await os.path.isfile(file)) or await os.path.isfile('flows/'+file.replace('/', ''))
            except (KeyError, AssertionError) as e:pass
            else:
                try:
                    if not (await os.path.isfile(file)):file = glob.glob(f'./**/{file}', recursive=True)[0]
                    async with aiofiles.open(file) as f:code = await f.read()
                    fg = ''.join(random.sample(string.ascii_letters+string.digits, k=LENGTH_OF_ID)) + '.py'
                    async with aiofiles.open(fg, 'w') as f:await f.write(code)
                    await os.remove(fg)
                    g = {i:v for i,v in globals().items()}
                    g['DATA'] = data
                    if threaded:await asyncio.to_thread(exec, [code, g, locals()])
                    else:exec(code, g, locals())
                    print(f'Flow {flow} executed {file} given type data {t} on {datetime.datetime.now(datetime.UTC)} UTC.')
                except Exception as e:print(f'Error when executing function for flow {flow}: {str(e)}')
                try:
                    if dat.get('address') is not None:
                        async with session.post(dat['address'], data=json.dumps(data)) as _:pass
                        print(f'Flow {flow} send {dat["address"]} type data {t} on {datetime.datetime.now(datetime.UTC)} UTC.')
                except Exception as e:
                    print(f'Error in POSTing JSON data: {str(e)}')
                print(f'Flow {flow} finished on {datetime.datetime.utcnow()} UTC.')
            
def load_flows():
    global FLOWS
    try:
        #__import__('os').remove('flows.pickle') # sept 2024, why is this here?
        with open('flows.pickle', 'rb') as f:
            FLOWS = pickle.load(f)
        
    except Exception as e:
        print(f'Error loading flows in db_funcs: {str(e)}')

async def rm_files_ids(ids: list[str] | tuple[str] | set[str], fps_passed: bool=False):
    """Removes all files to the corresponding post ids provided.
    :param ids: file paths to files, or post ids."""
    ids = (i[-5] for i in await get_posts() if i[0] in ids) if not(fps_passed) else ids
    for i in ids:
        if i is not None: #used to be isinstance of str
            match = re.match(F'^([a-zA-Z0-9]{{{LENGTH_OF_ID}}})_', i)
            if (await os.path.isfile(i)) and match!=None:
                await os.remove(i)
                
async def start_conn():
    global cursor, session
    
    cursor = await aiosqlite.connect(DATABASE)
    # locale = {'.\\database.sqlite3', '.\\rep_reg.py', '.\\script.js', '.\\db_funcs.py', '.\\requirements.txt', '.\\backend.py', '.\\LICENSE', '.\\__main__.py', '.\\backup.sqlite3', '.\\maintenence', '.\\clear.py', '.\\tests', '.\\__pycache__', '.\\Privacy Policy', '.\\README.md', '.\\user.jpeg', '.\\inject.sqlite3'}
    posts = await get_posts()
    session = aiohttp.ClientSession(loop=asyncio.get_event_loop())
    files = {i[-5] for i in posts}
    for i in glob.glob('*'):
        match = re.match(f'^([a-zA-Z0-9]{{{LENGTH_OF_ID}}}_)', i)
        if (await os.path.isfile(i)) and match!=None:#cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg
            if not i in files:
                await os.remove(i)
    
async def back(to: str):
    """Backups the main database to the database fp provided."""
    await cursor.commit()
    to: aiosqlite.Connection = await aiosqlite.connect(to)
    await cursor.backup(to)
    await to.commit()
    await to.close()
    del to


async def get_posts() -> tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]:
    """Returns list[tuple[str, str, str, set[str], set[str]]]. Representing an id, title, content, date, file path, IP, pin, upvotes, and downvotes"""
    res = await cursor.execute("SELECT * FROM posts")
    res = reversed(await res.fetchall())
    return [
        (*((i)[0:7]), ast.literal_eval(i[-2]), ast.literal_eval(i[-1])) for i in res
    ]


async def get_post(id: str) -> tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]:
    """Returns tuple[str, str, str]. Representing a id, title, content, date, IP, file path, pin, upvotes, and downvotes."""
    res = await cursor.execute("SELECT * FROM posts WHERE id=?", [id])
    res = await res.fetchone()
    return (*((res)[0:7]), ast.literal_eval(res[-2]), ast.literal_eval(res[-1]))


async def start():
    """Restarts the production database."""
    if (
        "y"
        in input("Continuing will restart database.sqlite3, proceed? (Y/N): ").lower()
    ):
        if "y" in input("Backup current state? (Y/N): ").lower():
            await back(BACKUP)
        await (
            await (
                await (await cursor.execute("DROP TABLE IF EXISTS posts;")).execute(
                    "DROP TABLE IF EXISTS ips;"
                )
            ).execute(
                "CREATE TABLE posts(id TEXT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, fp TEXT NULL, ip TEXT NOT NULL, pin TEXT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
            )
        ).execute("CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);")

        print("Cleared database.")
    else:
        print("Cancelling")
    await update_inject()


async def update_inject():
    """Updates the inject database to check if a query is an inject. Should be run after updating the main database."""
    await cursor.commit()
    await back(INJECT)
    # print('Started inject testing database.')

async def setup_dbs():
    '''Clears all databases with no prompts.'''
    global cursor
    await (
        await (
            await (await cursor.execute("DROP TABLE IF EXISTS posts;")).execute(
                "DROP TABLE IF EXISTS ips;"
            )
        ).execute(
            "CREATE TABLE posts(id TEXT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, fp TEXT NULL, ip TEXT NOT NULL, pin TEXT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
        )
    ).execute("CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);")
    await cursor.commit()
    await back(BACKUP)
    await back(INJECT)
    

async def new_post(
    title: str,
    content: str,
    date: datetime.datetime | str,
    ip: str,
    fp: str | None = None,
    pin: str | None=None,
    upvotes: set | None = {},
    downvotes: set | None = {}
    
) -> tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]:
    """Creates a new post with provided data, returns the row in the database as a tuple."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    id = "".join(random.sample(string.ascii_letters+string.digits, k=LENGTH_OF_ID))
    try:
        upvotes = (ast.literal_eval(str(upvotes)))
        downvotes = (ast.literal_eval(str(downvotes)))
    except Exception:
        pass
    # while True:
    #     try:
    #         await get_post(id)
    #     except Exception as e:
    #         if isinstance(e, TypeError):
    #             break
    #         id = "".join(random.sample(string.ascii_letters+string.digits, k=6))
    await cursor.execute(
        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
        [id, title, content, date, fp, ip, pin, f"{upvotes}", f"{downvotes}"],
    )
    d = (id, title, content, date, fp, ip, pin, upvotes, downvotes)
    await handler(d, 2, True)
    return d


async def delete_ip(ip: str) -> tuple[str, int]:
    """Removes an IP address from the database. Returns the row as a tuple before deletion."""
    res = tuple(
        await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone()
    )
    await cursor.execute("DELETE FROM ips WHERE ip=?", [ip])
    return res


async def add_ip(ip: str, blacklisted: bool = False) -> tuple[str, int]:
    """Adds an IP address to the database. Returns the row as a tuple."""
    await cursor.execute("INSERT INTO ips VALUES (?, ?)", (ip, int(blacklisted)))
    return (ip, int(blacklisted))

async def update_ip(ip: str, blacklisted: bool) -> tuple[str, int]:
    """Updates an IP address in the database. Returns the row as a tuple."""
    await cursor.execute(
        "UPDATE ips SET ip=?, blacklisted=?  WHERE ip=?;", (ip, int(blacklisted), ip)
    )
    return (ip, int(blacklisted))


async def get_ips() -> list[tuple[str, int]]:
    """Returns all the ip addresses in the database."""
    return list(await (await cursor.execute("SELECT * FROM ips")).fetchall())


async def get_ip(ip: str) -> tuple[str, int]:
    """Return the ip addresses from the database."""
    res = tuple(
        await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone()
    )
    return res


async def delete_post(
    id: str,
) -> tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]:
    """Removes a post by it's id from the database, returns the database row as a tuple before deletion."""
    post = await get_post(id)
    await cursor.execute("DELETE FROM posts WHERE id=?;", [id])
    await rm_files_ids((post[-5], ), True)
    await handler(post, 3, True)
    return post

# async def delete_posts(
#     ids: typing.Iterable[str],
# ) -> typing.AsyncGenerator[tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]], None,]:
#     """Removes multiple posts by ids from the database, returns the database rows as a tuple before deletion."""
#     ids = {i for i in (await get_posts()) if i[0] in ids}  # type: ignore
#     await rm_file_ids((i[-5] for i in ids), True)
#     p = map((lambda x: (x[0], (*x[1:5], *x[6:-2], len(x[-1])-len(x[-2])))), filter((lambda x: x[0] in ids), await get_posts()))
#     await handler(dict(p), 3)
#     for post in ids:
#         await cursor.execute("DELETE FROM posts WHERE id=?;", [post[0]])
#         yield post  # type: ignore

async def delete_posts(
    ids: typing.Iterable[str],
) -> typing.AsyncGenerator[tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]], None,]:
    """Removes multiple posts by ids from the database, returns the database rows as a tuple before deletion."""
    
    for post in ids:
        yield await delete_post(post)


async def update_post(
    id: str,
    title: str,
    content: str,
    date: datetime.datetime | str,
    upvotes: set[str],
    downvotes: set[str],
    fp: str | None = None,
    ip: str | None=None,
    pin: str|None=None,

) -> tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]:
    """Updates a post with the arguments provided."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    await cursor.execute(
        "UPDATE posts SET id=?,title=?,content=?,date=?,fp=?,ip=?, pin=?, upvotes=?, downvotes=? WHERE id=?",
        [id, title, content, date, fp, ip, pin, f'{upvotes}', f'{downvotes}', id],
    )
    return (id, title, content, date, fp, ip, pin, upvotes, downvotes)


async def start_backup():
    """Restarts the backup database."""
    if "y" in input("Restart backup database (Y/N)?: ").lower():
        cursor = await aiosqlite.connect(BACKUP)
        await (
            await (
                await (await cursor.execute("DROP TABLE IF EXISTS posts;")).execute(
                    "DROP TABLE IF EXISTS ips;"
                )
            ).execute(
                "CREATE TABLE posts(id TEXT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, fp TEXT NULL, ip TEXT NOT NULL, pin TEXT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
            )
        ).execute("CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);")
        await cursor.commit()
        await cursor.close()
        print("Backup deleted.")


async def is_inject(query: str) -> bool:
    """Returns whether or not a string query is an sql inject (not always accurate)."""
    try:
        await update_inject()
        con = await aiosqlite.connect(INJECT)
        await con.execute(query)
    except Exception as e:
        await con.close()
        await update_inject()
        
        return False
    else:
        await con.close()
        await update_inject()
        
        return True


async def add_upvote(ip: str, id: str):
    """Adds a upvote to post id provided."""
    post = await get_post(id)
    # order of post
    # id, title, content, date, fp, ip, pin, upvotes, downvotes
    # d = await update_post(
    #     id, post[1], post[2], post[3], ip, {*post[-2], ip}, post[-1], post[4], post[-3], 
    # )
    d = await rep_post(id, upvotes={*post[-2], ip}, post=post)
    await handler(d, 1, True)
    return d


async def remove_upvote(ip: str, id: str):
    """Removes an upvote from the id provided."""
    post = await get_post(id)
    upvotes = post[-2]
    try:
        upvotes.remove(ip)
    except Exception:
        pass
    # d = await update_post(
    #     id, post[1], post[2], post[3], ip, upvotes, post[-1], post[4], post[-3]
    # )
    d = await rep_post(id, upvotes=upvotes, post=post)
    await handler(d, 1, True)
    return d


async def add_downvote(ip: str, id: str):
    """Adds a downvote to post id provided."""
    post = await get_post(id)
    # d = await update_post(
    #     id, post[1], post[2], post[3], post[4], ip, post[6], post[-2], {*post[-1], ip}
    # )
    d= await rep_post(id, downvotes={*post[-1], ip}, post=post)
    await handler(d, 1, True)
    return d

async def remove_downvote(ip: str, id: str):
    """Removes an downvote from the id provided."""
    
    post = await get_post(id)
    downvotes = post[-1]
    try:
        downvotes.remove(ip)
    except Exception:
        pass
    d = await rep_post(ip, downvotes=downvotes, post=post)
    await handler(d, 1, True)
    return d


async def purge_ip(ip: str) -> list[tuple[str, str, str, str, str, str, set[str], set[str]]]:
    """Removes all posts from ip provided."""
    posts = await (
        await cursor.execute("SELECT * FROM posts WHERE ip=?", [ip])
    ).fetchall()
    await rm_files_ids((i[-5] for i in posts), True)
    await cursor.execute("DELETE FROM posts WHERE ip=?", [ip])
    p = map((lambda x: (x[0], (*x[1:5], *x[6:-2], len(x[-1])-len(x[-2])))), filter((lambda x: x[0] in {i[-5] for i in posts}), await get_posts()))
    await handler(dict(p), 3)
    return posts # type: ignore


async def ban_author(id: str) -> str:
    """IP bans the author of a post id provided, returns the authors IP."""
    post = await get_post(id)
    
    ip = post[-4]
    
    if not await is_blacklisted(ip):
        await update_ip(ip, True)
    return ip


async def is_blacklisted(ip: str) -> bool:
    """Returns whether the IP in question is blacklisted or not."""
    if not any(i[0] == ip for i in await get_ips()):
        await add_ip(ip)
    return bool((await get_ip(ip))[1])

async def rep_post(
    id: str,
    title: str|None=None,
    content: str|None=None,
    date: datetime.datetime | str|None=None,
    ip: str|None=None,
    upvotes: set[str]|None=None,
    downvotes: set[str]|None=None,
    fp: str = None,
    pin: str=None,
    post: tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]|None=None
) -> tuple[str, str, str, str, str | None, str, str | None, set[str], set[str]]:
    """Updates only arguments of post that are provided, rest are not changed."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    if post is None:
        post = await get_post(id)
    query = [id, post[1] if title is None else title, post[2] if content is None else content, post[3] if date is None else date, None if fp == '' else (lambda: post[4] if fp is None else fp)(), post[5] if ip is None else ip, None if pin=='' else (lambda: post[6] if pin is None else pin)(), f'{post[7]}' if upvotes is None else f'{upvotes}', f'{post[8]}' if downvotes is None else f'{downvotes}', id]
    await cursor.execute(
        "UPDATE posts SET id=?,title=?,content=?,date=?,fp=?,ip=?,pin=?, upvotes=?, downvotes=? WHERE id=?", query, ) # we need fp and pin to be '' not None.
    query = query[:-1]
    return (query[:5], query[-2:], query[5:7])
    
async def close():
    """Closes connection to database."""
    global session
    await session.close()
    posts = await get_posts()
    files = {i[-5] for i in posts}
    for i in glob.glob('*'):
        match = re.match(f'^([a-zA-Z0-9]{{{LENGTH_OF_ID}}})_', i)
        if (await os.path.isfile(i)) and match!=None:#cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg
            if not i in files:
                # print('requirements met', i)
                await os.remove(i)
    await cursor.commit()
    await cursor.close()

async def create():
    'Creates inject, backup and database files.'
    global cursor
    try:
        await cursor.interrupt()
        await cursor.commit()
        await cursor.close()
    except Exception:
        pass
    for i in ['database.sqlite3', 'backup.sqlite3', 'inject.sqlite3']:
        if (await os.path.isfile(i)):await os.remove(i)
        async with aiofiles.open(i, 'x'):pass
        
    cursor = await aiosqlite.connect(DATABASE)
    await (
            await (
                await (await cursor.execute("DROP TABLE IF EXISTS posts;")).execute(
                    "DROP TABLE IF EXISTS ips;"
                )
            ).execute(
                "CREATE TABLE posts(id TEXT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, fp TEXT NULL, ip TEXT NOT NULL, pin TEXT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
            )
        ).execute("CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);")
    await back(BACKUP)
    await update_inject()
    await cursor.close()

if __name__ == "__main__":
    async def main():
        
        await start_conn()
        await start()
        await start_backup()
        if "y" in input("Perform database tests? (Y/N): ").lower():
            pickled: tuple[bytes] = pickle.load(open('./data.pickle', 'rb'))
            if not (await os.path.isfile('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg')):
                open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'x')
                open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'wb').write(pickled[0])
            if not (await os.path.isfile('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt')):
                open('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'x')
                open('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'wb').write(pickled[1])
            print(await get_posts(), await get_ips())
            await add_ip("", True)
            print(await is_blacklisted(""))
            print(*await get_ips())
            await update_ip("", False)
            print(*await get_ips())
            await delete_ip("")
            print(*await get_ips())
            # snip
            await new_post("", "", datetime.datetime.now(), "my_ip",)
            print(*await get_posts())
            await update_post(
                (await get_posts())[0][0],
                "t",
                "t",
                datetime.datetime.now(datetime.UTC),
                {"192.168.2.1",},
                {"127.0.0.1"},
                "test.txt",
                "192.168.2.1",
                'test pin 1',

            )
            print(*await get_posts())
            await add_upvote("rick roll", (await get_posts())[0][0])
            print(*await get_posts())
            await add_downvote("rick roll", (await get_posts())[0][0])
            print(*await get_posts())
            await remove_upvote("rick roll", (await get_posts())[0][0])
            print(*await get_posts())
            await remove_downvote("rick roll", (await get_posts())[0][0])
            print(*await get_posts())
            await delete_post((await get_posts())[0][0])
            print(*await get_posts())
            # snip
            await new_post('test post 2', 'test post 2', datetime.datetime.utcnow(), '192.168.2.1', 'cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'test pin')
            await new_post('test post 3', 'test post 3', '6969-69-69', '192.168.2.1', 'RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'test pin')
            await new_post('CONST', 'CONST', 'CONST', 'CONST', 'CONST', 'CONST')
            print(await rep_post(((await get_posts())[0][0]), pin='&#128392; Pinned by moderators'))
            print(*await get_posts())
            print((await get_posts())[-1][0])
            await ban_author((await get_posts())[-1][0])
            post = await get_post((await get_posts())[-1][0])
            if post is None:
                print('Author CONST was banned.')
            print(await is_blacklisted('CONST'))
            print(*await get_posts(), *await get_ips())
            await purge_ip('192.168.2.1')
            print(*await get_posts(), *await get_ips())
            await purge_ip('CONST')
            print(*await get_posts(), *await get_ips())
            print(await is_inject("SELECT * FROM posts"))
            print(await is_inject("hello!"))
            #await start_conn()
            
            open('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'x')
            open('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'wb').write(pickled[1])
            open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'x')
            open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'wb').write(pickled[0])
        await close()
            
    asyncio.run(main())
