"""Run the pinned upstream add-on with an explicit main-thread queue pump."""
import importlib.util
import os
from pathlib import Path
import signal
import socket
import sys
import threading
import time
import bpy

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('blendermcp', root / 'external/mcp-for-blender/addon.py')
addon = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = addon
spec.loader.exec_module(addon)
addon.register()
# Headless mode has no UI event loop. Do not pretend its timers will run.
addon._blendermcp_unregister_auto_start()
if bpy.app.timers.is_registered(addon._addon_update_check_on_startup):
    bpy.app.timers.unregister(addon._addon_update_check_on_startup)
server = addon.BlenderMCPServer(host='127.0.0.1', port=int(os.environ.get('BLENDER_PORT', '9876')))
server.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.socket.bind((server.host, server.port))
server.socket.listen(5)
server.running = True
server.server_thread = threading.Thread(target=server._server_loop, daemon=True)
server.server_thread.start()
def shutdown(*_):
    server.running = False
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)
print(f'HEADLESS_MCP_READY {server.host}:{server.port}', flush=True)
try:
    while server.running:
        server._drain_command_queue()
        time.sleep(0.01)
finally:
    server.stop()
