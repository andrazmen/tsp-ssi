async def check_agent():
    result = await client.server.check_liveliness()

    print(result)
    return result