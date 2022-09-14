# this is to be run on workflows to prevent accidental doxxing.
from db_funcs import *
cursor.execute('DROP TABLE IF EXISTS posts;').execute('DROP TABLE IF EXISTS ips;').execute('CREATE TABLE posts(id INT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL);').execute('CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);')
with open(DATABASE, 'rb') as db:
    with open(INJECT, 'wb') as inj:
        inj.write(db.read())
tmp = sqlite3.connect(BACKUP)
tmp.execute('DROP TABLE IF EXISTS posts;').execute('CREATE TABLE posts(id INT PRIMARY KEY NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,date TEXT NOT NULL);').execute('DROP TABLE IF EXISTS ips;').execute('CREATE TABLE ips(ip TEXT PRIMARY KEY NOT NULL, blacklisted INT);')
tmp.commit()
tmp.close()
cursor.commit()
cursor.close()
