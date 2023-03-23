import fastapi
app = fastapi.FastAPI()

@app.patch('/')
async def recieve(data=fastapi.Body()):
    print('Recieved data', data)