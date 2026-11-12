"""Launch pinned MCP; --headless owns a Blender subprocess in the same runtime."""
import os
import types
from pathlib import Path
import socket
import subprocess
import sys
import time
root = Path(__file__).resolve().parents[1]
os.environ.setdefault('BLENDER_HOST', '127.0.0.1')
os.environ.setdefault('BLENDER_MCP_DISABLE_TELEMETRY', '1')
sys.path.insert(0, str(root / 'external/mcp-for-blender/src'))

def run():
    proc = None
    if '--headless' in sys.argv:
        sys.argv.remove('--headless')
        # A private port avoids collisions and keeps the owned process isolated.
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            os.environ['BLENDER_PORT'] = str(probe.getsockname()[1])
        proc = subprocess.Popen([os.environ.get('BLENDER_BIN', 'blender'), '--background', '--factory-startup', '--python', str(root/'scripts/blender_headless.py')], stdout=sys.stderr, stderr=sys.stderr)
        try:
            deadline = time.monotonic() + 30
            while True:
                if proc.poll() is not None:
                    raise RuntimeError('Blender exited before connection')
                try:
                    with socket.create_connection(('127.0.0.1', int(os.environ['BLENDER_PORT'])), timeout=.2):
                        break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('Blender startup timed out')
                    time.sleep(.1)
        except BaseException:
            proc.terminate()
            proc.wait(timeout=10)
            raise
    try:
        # Upstream excludes config.py from Git. Supply an explicitly disabled
        # configuration for source checkouts; no telemetry endpoint or key.
        config = types.ModuleType('blender_mcp.config')
        config.telemetry_config = types.SimpleNamespace(
            enabled=False, max_prompt_length=0, supabase_anon_key='',
            supabase_bucket='', supabase_url='', timeout=5)
        sys.modules['blender_mcp.config'] = config
        from blender_mcp.server import main
        main()
    finally:
        if proc is not None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

if __name__ == '__main__':
    run()
