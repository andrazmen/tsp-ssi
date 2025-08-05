async def check_agent():
    result = await client.server.check_liveliness()
    print(result)
    return result

async def get_config():
    result = await client.server.get_config
    print(result)
    return result