import fastapi
app = fastapi.FastAPI()

@app.post('/')
async def recieve(data=fastapi.Body()):
    print('Recieved data', data)