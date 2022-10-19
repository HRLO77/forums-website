#!/usr/bin/python
# -*- coding: utf-8 -*-

# make sure to run this file with python __main__.py --user to start up the server and api properly (local).
import os
import socket
import uvicorn
import sys
# print(sys.argv)

if sys.argv[1] == 'True':
    os.system(f"echo {socket.gethostbyname(socket.gethostname())} is my ip address")
    uvicorn.run('backend:app', host=socket.gethostbyname(socket.gethostname()), port=8080)
else:
    uvicorn.run('backend:app')