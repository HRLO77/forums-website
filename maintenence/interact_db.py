# this is for usage to interact with the database through new commands or prexisting functions
import difflib
import os
import sys
import inspect
import asyncio

os.chdir("..")
sys.path.append(os.getcwd())
from db_funcs import *  # let the chaos ensue


def fmt_function(func):
    args = inspect.signature(func).parameters
    return (
        "\nfunction "
        + func.__name__
        + ":\nParams: ("
        + ", ".join((f"{args[i]}" for i in args.keys()))
        + ")\n - "
        + func.__doc__
        + "\n-----------------------\n"
    )


def parse_and_lookup(s: str):
    i = s.split()
    try:
        return globals()[i[1]]
    except KeyError:
        print("Function does not exist.")
        print(
            "Closest functions are - ",
            ", ".join(
                difflib.get_close_matches(i[1], [v[0] for v in globals().items()])
            ),
        )
        return None


async def main():
    await start_conn()
    while True:
        try:
            i = input(
                "Enter --command <*args> to run a function and provide arguments, --doc <function> to list arguments for a function and docs, or enter anything else (run as an SQL command on the db): "
            )
            if i == "cls" or i == "clear":
                os.system("cls||clear")
                continue
            if i.startswith("--doc"):
                lookup = parse_and_lookup(i)
                if lookup is None:
                    continue
                print(fmt_function(lookup))
                continue
            if i.startswith("--command"):
                lookup = parse_and_lookup(i)
                if lookup is None:
                    continue
                try:
                    args = i.removeprefix("--command").split()[1:]
                except Exception:
                    args = []
                try:
                    print(await lookup(*args))
                except Exception as e:
                    print("Error:", e)
                continue
            else:
                try:
                    print(await (await cursor.execute(i)).fetchall())
                except Exception as e:
                    print("Error:", e)

        except KeyboardInterrupt:
            print("Admin session finished.")
            break
    await close()


asyncio.run(main())
