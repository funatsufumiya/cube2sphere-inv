__author__ = 'Xyene'


import bpy
import sys
import math

# 引数取得（末尾から順に）
output_path = sys.argv[-1]
res_y = int(sys.argv[-2])
res_x = int(sys.argv[-3])
faces = {
    'front': sys.argv[-4],
    'back': sys.argv[-5],
    'left': sys.argv[-6],
    'right': sys.argv[-7],
    'top': sys.argv[-8],
    'bottom': sys.argv[-9],
}

scene = bpy.context.scene
scene.render.resolution_x = res_x
scene.render.resolution_y = res_y
scene.render.resolution_percentage = 100
scene.render.filepath = output_path

# 球体作成
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1, location=(0,0,0))
sphere = bpy.context.active_object

# マテリアル作成
mat = bpy.data.materials.new(name="Cube2SphereMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# ノード初期化
for n in nodes:
    nodes.remove(n)
output = nodes.new(type='ShaderNodeOutputMaterial')
mix = nodes.new(type='ShaderNodeMixShader')
emission = nodes.new(type='ShaderNodeEmission')

# 6面画像テクスチャノード作成
tex_nodes = {}
for key in faces:
    img = bpy.data.images.load(faces[key])
    tex = nodes.new(type='ShaderNodeTexEnvironment')
    tex.image = img
    tex_nodes[key] = tex

# 6面方向ごとにマッピング（簡易: front/back/left/right/top/bottomをMixで合成）
# 本来は方向ごとに座標判定してMixする必要あり
mix.inputs[0].default_value = 0.5
links.new(tex_nodes['front'].outputs[0], emission.inputs[0])
links.new(emission.outputs[0], mix.inputs[1])
links.new(tex_nodes['back'].outputs[0], mix.inputs[2])
links.new(mix.outputs[0], output.inputs[0])

# 球体にマテリアル割り当て
if sphere.data.materials:
    sphere.data.materials[0] = mat
else:
    sphere.data.materials.append(mat)

# カメラ位置調整（原点から球体全体を撮影）
camera = bpy.data.objects['Camera']
camera.location = (0, 0, 0)
camera.rotation_mode = 'XYZ'
camera.rotation_euler = (0, 0, 0)
# Equirectangularパノラマ設定（Blenderバージョンごとに分岐）
blender_version = bpy.app.version[0]
camera.data.type = 'PANO'
if blender_version >= 5:
    camera.data.panorama_type = 'EQUIRECTANGULAR'
else:
    camera.data.cycles.panorama_type = 'EQUIRECTANGULAR'

# レンダリング
bpy.ops.render.render(write_still=True)
