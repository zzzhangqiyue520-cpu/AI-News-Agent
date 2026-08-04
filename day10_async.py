import asyncio


async def task(name):

    print(name,"开始")

    await asyncio.sleep(3)

    print(name,"完成")


async def main():

    await asyncio.gather(
        task("A"),
        task("B"),
        task("C")
    )


asyncio.run(main())