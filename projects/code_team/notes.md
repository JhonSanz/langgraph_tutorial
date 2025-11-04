# # from claude_agent_sdk import query
# # import asyncio


# # def basic_mcp():
# #     """
# #     Función básica para probar MCP filesystem.
# #     """

# #     async def run_test():
# #         async for message in query(
# #             prompt="List all Python files in my project",
# #             options=ClaudeAgentOptions(
# #                 mcp_servers={
# #                     "filesystem": {
# #                         "command": "npx",
# #                         "args": ["@modelcontextprotocol/server-filesystem"],
# #                         "env": {"ALLOWED_PATHS": "/Users/me/projects"},
# #                     }
# #                 },
# #                 allowed_tools=[
# #                     "Read",
# #                     "Write",
# #                     "Edit",
# #                     "MultiEdit",
# #                     "Grep",
# #                     "Glob",
# #                     "mcp__filesystem__list_files",
# #                 ],
# #             ),
# #         ):
# #             print(message)

# #     asyncio.run(run_test())


# if __name__ == "__main__":
#     print("=" * 60)
#     print("  Product Manager - Generador de User Stories")
#     print("=" * 60)
#     asyncio.run(product_manager_node_async())
#     print("\n" + "=" * 60)
#     print("  Proceso finalizado")
#     print("=" * 60)
