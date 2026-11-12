"""End-to-end MCP check; uses a disposable Blender scene."""
import asyncio
import json
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(Path(__file__).with_name('run_mcp.py')), '--headless'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            names = [t.name for t in listing.tools]
            assert 'execute_blender_code' in names
            print('MCP_HANDSHAKE_OK', len(names))
            result = await session.call_tool('get_addon_status', {})
            status_text = result.model_dump_json()
            assert not result.isError and 'Error checking' not in status_text and 'protocol_version' in status_text, status_text
            print('ADDON_STATUS', result.model_dump_json())
            code = '''import bpy
name = "MCP_Connection_Probe"
assert bpy.data.objects.get(name) is None, "Probe name already exists"
mesh = bpy.data.meshes.new(name)
mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)])
obj = bpy.data.objects.new(name, mesh)
bpy.context.scene.collection.objects.link(obj)
group = bpy.data.node_groups.new("GN_MCP_Probe", "GeometryNodeTree")
group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
i = group.nodes.new("NodeGroupInput")
o = group.nodes.new("NodeGroupOutput")
group.links.new(i.outputs["Geometry"], o.inputs["Geometry"])
mod = obj.modifiers.new("Probe", "NODES")
mod.node_group = group
bpy.context.view_layer.update()
assert len(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.polygons) == 1
print("MESH_AND_GEOMETRY_NODES_OK")
bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.meshes.remove(mesh)
bpy.data.node_groups.remove(group)
print("PROBE_CLEANUP_OK")'''
            result = await session.call_tool('execute_blender_code', {'code': code})
            text = result.model_dump_json()
            assert not result.isError and 'MESH_AND_GEOMETRY_NODES_OK' in text and 'PROBE_CLEANUP_OK' in text, text
            print(text)
            print('END_TO_END_OK')

if __name__ == '__main__':
    asyncio.run(main())
