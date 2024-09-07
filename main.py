# make sure to run this file with `python main.py --user {YOUR_MODERATION_PASSWORD}` to start up the server and api properly (local).
import uvicorn
import sys
import os
uvicorn.run('backend:app', host='127.0.0.1', port=8000) # edit this line to change what interface and port the server binds to
exit()
if sys.argv[1] == 'True':
    uvicorn.run('backend:app', host=os.environ['DETA_SPACE_APP_HOSTNAME'], port=8000) # edit this line to change what interface and port the server binds to
else:
    uvicorn.run('backend:app')