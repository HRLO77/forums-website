from db_funcs import *
import asyncio
async def main():
    await start_conn()
    print(await rep_post('ID HERE!', pin='&#128392; Pinned'))
    await close()
asyncio.run(main())