import sqlite3
import asyncio
import typing
import datetime
import random

DATABASE = "./database.sqlite3"
BACKUP = "./backup.sqlite3"
INJECT = "./inject.sqlite3"
cursor = sqlite3.connect(DATABASE)


def get_posts() -> list[tuple[int, str, str, str]]:
    """Returns list[tuple[str, str, str]]. Representing a title, content and date."""
    res = cursor.execute("SELECT * FROM posts")
    return res.fetchall()


def get_post(id: int) -> tuple[int, str, str, str]:
    """Returns tuple[str, str, str]. Representing a title, content and date."""
    res = cursor.execute("SELECT id,title,content,date FROM posts WHERE id=?", [id])
    return res.fetchone()


def start():
    """Restarts the production database."""
    if (
        "y"
        in input("Continuing will restart database.sqlite3, proceed? (Y/N): ").lower()
    ):
        if "y" in input("Backup current state? (Y/N): ").lower():
            with open(DATABASE, "rb") as db:
                with open(BACKUP, "wb") as w:
                    w.write(db.read())
        cursor.execute("DROP TABLE IF EXISTS posts;").execute(
            "DROP TABLE IF EXISTS ips;"
        ).execute(
            "CREATE TABLE posts(id INT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL);"
        ).execute(
            "CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);"
        )

        print("Cleared database.")
    else:
        print("Cancelling")
    update_inject()


def update_inject():
    """Updates the inject database to check if a query is an inject. Should be run after updating the main database."""
    with open(DATABASE, "rb") as db:
        with open(INJECT, "wb") as inj:
            inj.write(db.read())
    # print('Started inject testing database.')


def new_post(
    title: str, content: str, date: datetime.datetime | str
) -> tuple[int, str, str, str]:
    """Creates a new post with provided data, returns the row in the database as a tuple."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    id = random.randint(0, 2147483646)
    while True:
        try:
            get_post(id)
        except sqlite3.DataError:
            id = random.randint(0, 2147483646)
        else:
            break
    cursor.execute("INSERT INTO posts VALUES (?, ?, ?, ?);", [id, title, content, date])
    update_inject()
    return cursor.execute(
        "SELECT id,title,content,date,id FROM posts WHERE id=?;", [id]
    ).fetchone()


def delete_ip(ip: str) -> tuple[str, int]:
    """Removes an IP address from the database. Returns the row as a tuple before deletion."""
    res = cursor.execute("SELECT * FROM ips WHERE ip=?", [ip]).fetchone()
    cursor.execute("DELETE FROM ips WHERE ip=?", [ip])
    update_inject()
    return res


def add_ip(ip: str, blacklisted: bool = False) -> tuple[str, int]:
    """Adds an IP address to the database. Returns the row as a tuple."""
    cursor.execute("INSERT INTO ips VALUES (?, ?)", (ip, int(blacklisted)))
    update_inject()
    return cursor.execute("SELECT * FROM ips WHERE ip=?", [ip]).fetchone()


def update_ip(ip: str, blacklisted: bool) -> tuple[str, int]:
    """Updates an IP address in the database. Returns the row as a tuple."""
    cursor.execute(
        "UPDATE ips SET ip=?, blacklisted=?  WHERE ip=?;", (ip, int(blacklisted), ip)
    )
    update_inject()
    return cursor.execute("SELECT * FROM ips WHERE ip=?", [ip]).fetchone()


def get_ips() -> list[tuple[str, int]]:
    """Returns all the ip addresses in the database."""
    return cursor.execute("SELECT * FROM ips").fetchall()


def get_ip(ip: str) -> tuple[str, int]:
    """Return the ip addresses from the database."""
    res = cursor.execute("SELECT * FROM ips WHERE ip=?", [ip]).fetchone()
    return res


def delete_post(id: int) -> tuple[int, str, str, str]:
    """Removes a post by it's id from the database, returns the database row as a tuple before deletion."""
    post = get_post(id)
    cursor.execute("DELETE FROM posts WHERE id=?;", [id])
    update_inject()
    return post


async def to_thread(func: typing.Callable, *args, **kwargs):
    """Runs a blocking function on another thread and returns the result."""
    return await asyncio.to_thread(func, *args, **kwargs)


def update_post(
    id: int, title: str, content: str, date: datetime.datetime | str
) -> tuple[int, str, str, str]:
    """Updates a post with the arguments provided."""
    date = date.strftime("%Y-%m-%d") if isinstance(date, datetime.datetime) else date
    cursor.execute(
        "UPDATE posts SET id=?,title=?,content=?,date=? WHERE id=?",
        [id, title, content, date, id],
    )
    return get_post(id)


def start_backup():
    """Restarts the backup database."""
    if "y" in input("Restart backup database (Y/N)?: ").lower():
        tmp = sqlite3.connect(BACKUP)
        tmp.execute("DROP TABLE IF EXISTS posts;").execute(
            "CREATE TABLE posts(id INT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL);"
        ).execute("DROP TABLE IF EXISTS ips;").execute(
            "CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);"
        )
        tmp.commit()
        tmp.close()
        print("Backup deleted.")


def is_inject(query: str) -> bool:
    """Returns whether or not a string query is an sql inject (not always accurate)."""
    try:
        con = sqlite3.connect(INJECT)
        cur = con.cursor()
        cur.executescript(query)
        cur.execute(query)
    except Exception as e:
        return False
    else:
        return True


def is_blacklisted(ip: str) -> bool:
    """Returns whether the IP in question is blacklisted or not."""
    if not any(i[0] == ip for i in get_ips()):
        add_ip(ip)
    return bool(get_ip(ip)[1])


def close():
    """Closes connection to database."""
    cursor.commit()
    cursor.close()


if __name__ == "__main__":
    start()
    start_backup()
    if "y" in input("Perform database tests? (Y/N)"):
        print(get_posts(), get_ips())
        add_ip("", True)
        print(is_blacklisted(""))
        print(*get_ips())
        update_ip("", False)
        print(*get_ips())
        delete_ip("")
        print(*get_ips())
        # snip
        new_post("", "", datetime.datetime.now())
        print(*get_posts())
        update_post(get_posts()[0][0], "t", "t", datetime.datetime.utcnow())
        print(*get_posts())
        delete_post(get_posts()[0][0])
        print(*get_posts())
        print(is_inject("SELECT * FROM posts"))
        print(is_inject("hello!"))
