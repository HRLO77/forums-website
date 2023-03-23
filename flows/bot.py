import asyncio

async def main(data):
    print(globals(), 'are my globals')
    print(locals(), 'are my locals!')
    print(f'I recieved data {data}')
    print('Hello!')
    return
print('I have been loaded!')