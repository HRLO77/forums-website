import sqlite3
import asyncio
import typing
import datetime
import random
import ast
import string
import aiosqlite

DATABASE = "./database.sqlite3"
BACKUP = "./backup.sqlite3"
INJECT = "./inject.sqlite3"
cursor = None

async def start_conn():
    global cursor
    cursor = await aiosqlite.connect(DATABASE)


async def back(to: str):
    """Backups the main database to the database fp provided."""
    to: aiosqlite.Connection = await aiosqlite.connect(to)
    await cursor.backup(to)
    await to.commit()
    await to.close()
    del to


async def get_posts() -> list[tuple[str, str, str, str, set[str], set[str]]]:
    """Returns list[tuple[str, str, str, set[str], set[str]]]. Representing a title, content date, upvotes, and downvotes"""
    res = await cursor.execute("SELECT * FROM posts")
    res = await res.fetchall()
    return [
        (*((i)[0:4]), ast.literal_eval(i[-2]), ast.literal_eval(i[-1])) for i in res
    ]


async def get_post(id: str) -> tuple[str, str, str, str, set[str], set[str]]:
    """Returns tuple[str, str, str]. Representing a title, content date, upvotes, and downvotes."""
    res = await cursor.execute("SELECT * FROM posts WHERE id=?", [id])
    res = await res.fetchone()
    return (*((res)[0:4]), ast.literal_eval(res[-2]), ast.literal_eval(res[-1]))


async def start():
    """Restarts the production database."""
    if (
        "y"
        in input("Continuing will restart database.sqlite3, proceed? (Y/N): ").lower()
    ):
        if "y" in input("Backup current state? (Y/N): ").lower():
            await back(BACKUP)
        await (await (await (await cursor.execute("DROP TABLE IF EXISTS posts;")).execute("DROP TABLE IF EXISTS ips;")).execute("CREATE TABLE posts(id TEXT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
        )).execute(
            "CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);"
        )

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
    title: str, content: str, date: datetime.datetime | str
) -> tuple[str, str, str, str]:
    """Creates a new post with provided data, returns the row in the database as a tuple."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    id = ''.join(random.sample(string.ascii_letters, k=52))
    while True:
        try:
            await get_post(id)
        except Exception as e:
            if isinstance(e, TypeError):
                break
            id = ''.join(random.sample(string.ascii_letters, k=52))
        else:
            break
    await cursor.execute(
        "INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?);",
        [id, title, content, date, "{}", "{}"],
    )
    await update_inject()
    return tuple(await (await cursor.execute("SELECT * FROM posts WHERE id=?;", [id])).fetchone())


async def delete_ip(ip: str) -> tuple[str, int]:
    """Removes an IP address from the database. Returns the row as a tuple before deletion."""
    res = tuple(await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone())
    await cursor.execute("DELETE FROM ips WHERE ip=?", [ip])
    await update_inject()
    return res


async def add_ip(ip: str, blacklisted: bool = False) -> tuple[str, int]:
    """Adds an IP address to the database. Returns the row as a tuple."""
    await cursor.execute("INSERT INTO ips VALUES (?, ?)", (ip, int(blacklisted)))
    await update_inject()
    return tuple(await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone())


async def update_ip(ip: str, blacklisted: bool) -> tuple[str, int]:
    """Updates an IP address in the database. Returns the row as a tuple."""
    await cursor.execute(
        "UPDATE ips SET ip=?, blacklisted=?  WHERE ip=?;", (ip, int(blacklisted), ip)
    )
    await update_inject()
    return tuple(await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone())


async def get_ips() -> list[tuple[str, int]]:
    """Returns all the ip addresses in the database."""
    return list(await (await cursor.execute("SELECT * FROM ips")).fetchall())


async def get_ip(ip: str) -> tuple[str, int]:
    """Return the ip addresses from the database."""
    res = tuple(await (await cursor.execute("SELECT * FROM ips WHERE ip=?", [ip])).fetchone())
    return res


async def delete_post(id: str) -> tuple[str, str, str, str, set[str], set[str]]:
    """Removes a post by it's id from the database, returns the database row as a tuple before deletion."""
    post = await get_post(id)
    cursor.execute("DELETE FROM posts WHERE id=?;", [id])
    await update_inject()
    return post


async def to_thread(func: typing.Callable, *args, **kwargs):
    """Runs a blocking function on another thread and returns the result."""
    return await asyncio.to_thread(func, *args, **kwargs)


async def update_post(
    id: str,
    title: str,
    content: str,
    date: datetime.datetime | str,
    upvotes: set[str],
    downvotes: set[str],
) -> tuple[str, str, str, str, set[str], set[str]]:
    """Updates a post with the arguments provided."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    await cursor.execute(
        "UPDATE posts SET id=?,title=?,content=?,date=?, upvotes=?, downvotes=? WHERE id=?",
        [id, title, content, date, str(upvotes), str(downvotes), id],
    )
    await update_inject()
    return await get_post(id)


async def start_backup():
    """Restarts the backup database."""
    if "y" in input("Restart backup database (Y/N)?: ").lower():
        cursor = await aiosqlite.connect(BACKUP)
        await (await (await (await cursor.execute("DROP TABLE IF EXISTS posts;")).execute("DROP TABLE IF EXISTS ips;")).execute("CREATE TABLE posts(id TEXT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
        )).execute(
            "CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);"
        )
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
    await update_post(id, post[1], post[2], post[3], {*post[4], ip}, post[5])


async def remove_upvote(ip: str, id: str):
    """Removes an upvote from the id provided."""
    post = await get_post(id)
    upvotes = post[-2]
    try:
        upvotes.remove(ip)
    except Exception:
        pass
    await update_post(id, post[1], post[2], post[3], upvotes, post[5])


async def add_downvote(ip: str, id: str):
    """Adds a downvote to post id provided."""
    post = await get_post(id)
    await update_post(id, post[1], post[2], post[3], post[4], {*post[5], ip})


async def remove_downvote(ip: str, id: str):
    """Removes an downvote from the id provided."""
    post = await get_post(id)
    downvotes = post[-1]
    try:
        downvotes.remove(ip)
    except Exception:
        pass
    await update_post(id, post[1], post[2], post[3], post[4], downvotes)


async def is_blacklisted(ip: str) -> bool:
    """Returns whether the IP in question is blacklisted or not."""
    if not any(i[0] == ip for i in await get_ips()):
        await add_ip(ip)
    return bool((await get_ip(ip))[1])


async def close():
    """Closes connection to database."""
    await cursor.commit()
    await cursor.close()


if __name__ == "__main__":
    async def main():
        print(await is_inject('DROP TABLE posts;'))
        await start()
        await start_backup()
        if "y" in input("Perform database tests? (Y/N)").lower():
            print(await get_posts(), await get_ips())
            await add_ip("", True)
            print(await is_blacklisted(""))
            print(*await get_ips())
            await update_ip("", False)
            print(*await get_ips())
            await delete_ip("")
            print(*await get_ips())
            # snip
            await new_post("", "", datetime.datetime.now())
            print(*await get_posts())
            await update_post(
                (await get_posts())[0][0],
                "t",
                "t",
                datetime.datetime.utcnow(),
                {
                    "192.168.2.1",
                },
                {"127.0.0.1"},
            )
            print(*await get_posts())
            await add_upvote("rick roll", (await get_posts())[0][0])
            print(*await get_posts())
            await add_downvote("rick roll", (await get_posts())[0][0])
            print(*await get_posts())
            await delete_post((await get_posts())[0][0])
            print(*await get_posts())
            print(await is_inject("SELECT * FROM posts"))
            print(await is_inject("hello!"))
