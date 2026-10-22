import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            info = await session.initialize()
            print("SERVER:", info.server_info.name, info.server_info.version)
            print("PROTOCOL:", info.protocol_version)
            tools = await session.list_tools()
            print("TOOLS:", [t.name for t in tools.tools])
            for name, args in [
                ("network_status", {}),
                ("energy_report", {"period": "today"}),
                ("energy_report", {"period": "week"}),
                ("node_details", {}),
            ]:
                res = await session.call_tool(name, args)
                print(f"--- {name} {args} ---")
                for c in res.content:
                    print(c.text)


asyncio.run(main())
