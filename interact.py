from db_funcs import *
import asyncio
# "id": "jNWhMabQmFxJTCrvpuHecZgSlKVPBsIOnfqdoDyXGkAitzRYELwU", "pin": "&#128392; Pinned by moderators"
async def main():
    await start_conn()
    print(await rep_post('EmFxRQZdtoPYgLIVMGOiuHfqnpvNJlcbSXzehwWsBDkrKAaTUjCy', pin='&#128392; Pinned'))
    await close()
asyncio.run(main())