import os
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

DATABASE = "database.sqlite3"
BACKUP = "backup.sqlite3"
INJECT = "inject.sqlite3"
cursor: aiosqlite.Connection = aiosqlite.connect(DATABASE)
async def rm_files_ids(ids: list[str] | tuple[str] | set[str], fps_passed: bool=False):
    """Removes all files to the corresponding post ids provided.
    :param ids: file paths to files, or post ids."""
    ids = {i[-5] for i in await get_posts() if i[0] in ids} if not(fps_passed) else ids
    for i in ids:
        if isinstance(i, str):
            match = re.match('([a-zA-Z]{52})', i)
            if os.path.isfile(i) and match!=None:
                os.remove(i)
                
        
async def start_conn():
    global cursor
    cursor = await aiosqlite.connect(DATABASE)
    # locale = {'.\\database.sqlite3', '.\\rep_reg.py', '.\\script.js', '.\\db_funcs.py', '.\\requirements.txt', '.\\backend.py', '.\\LICENSE', '.\\__main__.py', '.\\backup.sqlite3', '.\\maintenence', '.\\clear.py', '.\\tests', '.\\__pycache__', '.\\Privacy Policy', '.\\README.md', '.\\user.jpeg', '.\\inject.sqlite3'}
    posts = await get_posts()
    files = {i[-5] for i in posts}
    for i in glob.glob('*'):
        match = re.match('^([a-zA-Z]{52})', i)
        if os.path.isfile(i) and match!=None:#cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg
            if not i in files:
                os.remove(i)
    

async def back(to: str):
    """Backups the main database to the database fp provided."""
    to: aiosqlite.Connection = await aiosqlite.connect(to)
    await cursor.backup(to)
    await to.commit()
    await to.close()
    del to


async def get_posts() -> list[tuple[str, str, str, str, str, str, str, set[str], set[str]]]:
    """Returns list[tuple[str, str, str, set[str], set[str]]]. Representing an id, title, content, date, file path, IP, pin, upvotes, and downvotes"""
    res = await cursor.execute("SELECT * FROM posts")
    res = reversed(await res.fetchall())
    return [
        (*((i)[0:7]), ast.literal_eval(i[-2]), ast.literal_eval(i[-1])) for i in res
    ]


async def get_post(id: str) -> tuple[str, str, str, str, str, str, str, set[str], set[str]]:
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


async def new_post(
    title: str,
    content: str,
    date: datetime.datetime | str,
    ip: str,
    fp: str | None = None,
    pin: str | None=None
) -> tuple[str, str, str, str, str, str, str, set[str], set[str]]:
    """Creates a new post with provided data, returns the row in the database as a tuple."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    id = "".join(random.sample(string.ascii_letters, k=52))
    while True:
        try:
            await get_post(id)
        except Exception as e:
            if isinstance(e, TypeError):
                break
            id = "".join(random.sample(string.ascii_letters, k=52))
    await cursor.execute(
        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
        [id, title, content, date, fp, ip, pin, "{}", "{}"],
    )
    await update_inject()
    return await get_post(id)


async def delete_ip(ip: str) -> tuple[str, int]:
    """Removes an IP address from the database. Returns the row as a tuple before deletion."""
    res = tuple(
        await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone()
    )
    await cursor.execute("DELETE FROM ips WHERE ip=?", [ip])
    await update_inject()
    return res


async def add_ip(ip: str, blacklisted: bool = False) -> tuple[str, int]:
    """Adds an IP address to the database. Returns the row as a tuple."""
    await cursor.execute("INSERT INTO ips VALUES (?, ?)", (ip, int(blacklisted)))
    await update_inject()
    return tuple(
        await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone()
    )


async def update_ip(ip: str, blacklisted: bool) -> tuple[str, int]:
    """Updates an IP address in the database. Returns the row as a tuple."""
    await cursor.execute(
        "UPDATE ips SET ip=?, blacklisted=?  WHERE ip=?;", (ip, int(blacklisted), ip)
    )
    await update_inject()
    return tuple(
        await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone()
    )


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
) -> tuple[str, str, str, str, str, str, str, set[str], set[str]]:
    """Removes a post by it's id from the database, returns the database row as a tuple before deletion."""
    post = await get_post(id)
    await cursor.execute("DELETE FROM posts WHERE id=?;", [id])
    await rm_files_ids({post[-5]}, True)
    await update_inject()
    return post

async def delete_posts(
    ids: typing.Iterable[str],
) -> typing.AsyncGenerator[tuple[str, str, str, str, str, str, str, set[str], set[str]], None,]:
    """Removes multiple posts by ids from the database, returns the database rows as a tuple before deletion."""
    ids = {i for i in (await get_posts()) if i[0] in ids}  # type: ignore
    await rm_file_ids({i[-5] for i in ids}, True) 
    for post in ids:
        await cursor.execute("DELETE FROM posts WHERE id=?;", [post[0]])
        await update_inject()
        yield post  # type: ignore


async def to_thread(func: typing.Callable, *args, **kwargs):
    """Runs a blocking function on another thread and returns the result."""
    return await asyncio.to_thread(func, *args, **kwargs)


async def update_post(
    id: str,
    title: str,
    content: str,
    date: datetime.datetime | str,
    ip: str,
    upvotes: set[str],
    downvotes: set[str],
    fp: str | None = None,
    pin: str|None=None
) -> tuple[str, str, str, str, str, str, str, set[str], set[str]]:
    """Updates a post with the arguments provided."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    await cursor.execute(
        "UPDATE posts SET id=?,title=?,content=?,date=?,fp=?,ip=?, pin=?, upvotes=?, downvotes=? WHERE id=?",
        [id, title, content, date, fp, ip, pin, f'{upvotes}', f'{downvotes}', id],
    )
    await update_inject()
    return await get_post(id)


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
        await update_inject()
        return False
    else:
        await update_inject()
        return True


async def add_upvote(ip: str, id: str):
    """Adds a upvote to post id provided."""
    post = await get_post(id)
    # order of post
    # id, title, content, date, fp, ip, pin, upvotes, downvotes
    return await update_post(
        id, post[1], post[2], post[3], ip, {*post[-2], ip}, post[-1], post[4], post[-3], 
    )


async def remove_upvote(ip: str, id: str):
    """Removes an upvote from the id provided."""
    post = await get_post(id)
    upvotes = post[-2]
    try:
        upvotes.remove(ip)
    except Exception:
        pass
    return await update_post(
        id, post[1], post[2], post[3], ip, upvotes, post[-1], post[4], post[-3]
    )


async def add_downvote(ip: str, id: str):
    """Adds a downvote to post id provided."""
    post = await get_post(id)
    return await update_post(
        id, post[1], post[2], post[3], ip, post[-2], {*post[-1], ip}, post[4], post[-3]
    )


async def remove_downvote(ip: str, id: str):
    """Removes an downvote from the id provided."""
    post = await get_post(id)
    downvotes = post[-1]
    try:
        downvotes.remove(ip)
    except Exception:
        pass
    return await update_post(
        id, post[1], post[2], post[3], ip, post[-2], downvotes, post[4], post[-3]
    )


async def purge_ip(ip: str) -> list[tuple[str, str, str, str, str, str, set[str], set[str]]]:
    """Removes all posts from ip provided."""
    posts = await (
        await cursor.execute("SELECT * FROM posts WHERE ip=?", [ip])
    ).fetchall()
    await rm_files_ids({i[-5] for i in posts}, True)
    await cursor.execute("DELETE FROM posts WHERE ip=?", [ip])
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
    fp: str | None = '',
    pin: str|None=None
) -> tuple[str, str, str, str, str, str, str, set[str], set[str]]:
    """Updates only arguments of post that are provided, rest are not changed."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    post = await get_post(id)
    await cursor.execute(
        "UPDATE posts SET id=?,title=?,content=?,date=?,fp=?,ip=?,pin=?, upvotes=?, downvotes=? WHERE id=?",
[id, post[1] if title is None else title, post[2] if content is None else content, post[3] if date is None else date, None if fp is None and post[4] is not None else (lambda: post[4] if fp is '' else fp)(), post[5] if ip is None else ip, post[6] if pin is None else pin, f'{post[7]}' if upvotes is None else f'{upvotes}', f'{post[8]}' if downvotes is None else f'{add_downvote}', id],
    )
    return await get_post(id)
    
async def close():
    """Closes connection to database."""
    posts = await get_posts()
    files = {i[-5] for i in posts}
    for i in glob.glob('*'):
        match = re.match('^([a-zA-Z]{52})', i)
        if os.path.isfile(i) and match!=None:#cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg
            if not i in files:
                # print('requirements met', i)
                os.remove(i)
    await cursor.commit()
    await cursor.close()

if __name__ == "__main__":
    async def main():
        
        await start_conn()
        await start()
        await start_backup()
        if "y" in input("Perform database tests? (Y/N): ").lower():
            pickled: tuple[bytes] = pickle.load(open('./data.pickle', 'rb'))
            if not os.path.isfile('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg'):
                open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'x')
                open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'wb').write(pickled[0])
            if not os.path.isfile('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt'):
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
                datetime.datetime.utcnow(),
                "192.168.2.1",
                {
                    "192.168.2.1",
                },
                {"127.0.0.1"},
                "test.txt", 'test pin 1'
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
            await close()
            open('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'x')
            open('RTSpMXFavdrLEuACcNZjhgmoqxHKbkGtDIeywQnYJWVBszPOUfli_requirements.txt', 'wb').write(pickled[1])
            open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'x')
            open('cREaxqyiMBHIXvQKWkVCJlDmdeuPNgoSrbhpjGfUzFAZYOsLnwtT_user.jpeg', 'wb').write(pickled[0])
            await start_conn()
            
    asyncio.run(main())
