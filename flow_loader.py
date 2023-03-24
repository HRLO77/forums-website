import asyncio, aiohttp, yaml, threading, subprocess, glob, aiofiles, pickle, json
from aiofiles import os
g = {}
EVENTS = {'*', 'vote', 'post', 'delete'}
for file in [*glob.glob('**/*.yaml', recursive=True),
             *glob.glob('**/*.yml', recursive=True)]:
    try:
        with open(file) as f:
            data = yaml.safe_load(f)
            name = [*data.keys()][0]
            if not (data[name]['event'].lower() in EVENTS):
                raise ValueError(f'{data[name]["event"]} is not a valid event in {EVENTS}')
            g.update(data)
    except Exception as e:
        print(f'Exception in loading flow {file}: {str(e)}')
with open('flows.pickle', 'wb') as f:
    pickle.dump(g, f)
print(f'{len(g.items())} Flows loaded successfully into flows.pickle!')
