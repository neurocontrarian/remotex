import sys

# --mcp-server: run the headless MCP server (stdio JSON-RPC) instead of the GUI.
# Intercepted here, before importing the Qt app, so no GUI/Qt code loads and
# nothing but JSON-RPC ever reaches stdout. This is how AI clients / mcpo drive
# a packaged build (AppImage / .app / .exe) — there is no loose mcp_server.py to
# point at, so the app binary itself launches the server:
#     Commandeck-Pro.AppImage --mcp-server
if "--mcp-server" in sys.argv[1:]:
    try:
        from commandeck_core.pro.mcp_server import main as _mcp_main
    except ImportError:
        sys.stderr.write("Commandeck: the MCP server requires Commandeck Pro.\n")
        sys.exit(1)
    _mcp_main()
else:
    from commandeck_qt.app import main
    main()
