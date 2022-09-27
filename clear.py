# this is to be run on workflows to prevent accidental doxxing.
from db_funcs import *

tp = sqlite3.connect("../top_level.sqlite3")
cursor.backup(tp)
tp.commit()
tp.close()
cursor.execute("DROP TABLE IF EXISTS posts;").execute(
    "DROP TABLE IF EXISTS ips;"
).execute(
    "CREATE TABLE posts(id INT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
).execute(
    "CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);"
)
update_inject()
tmp = sqlite3.connect(BACKUP)
tmp.execute("DROP TABLE IF EXISTS posts;").execute(
    "CREATE TABLE posts(id INT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL, upvotes TEXT NOT NULL, downvotes TEXT NOT NULL);"
).execute("DROP TABLE IF EXISTS ips;").execute(
    "CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);"
)
tmp.commit()
tmp.close()
cursor.commit()
cursor.close()
