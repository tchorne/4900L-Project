import bpy
import os
import math
import time

blend_dir = os.path.dirname(bpy.data.filepath)
project_dir = os.path.dirname(blend_dir)

outputs_dir = os.path.join(project_dir, "Python", "Outputs")
os.makedirs(outputs_dir, exist_ok=True)

inputs_dir = os.path.join(project_dir, "Python", "Inputs")
os.makedirs(inputs_dir, exist_ok=True)

object_map = {
    "Earth": "earth_normals",
    "defaultMaterial": "dragon_normals",
    "spot_triangulated": "spot_normals",
    "bunny": "bunny_normals",
}

base_color_map = {
    "Earth": "earth_albedo.png",
    "defaultMaterial": "dragon_albedo.png",
    "spot_triangulated": "spot_albedo.png",
    "bunny": "bunny_albedo.png",
}

filters = ["Default", "SLIC", "LayeredPaint", "Kuwahara"]

def load_image(path):
    if not os.path.exists(path):
        print(f"❌ Image not found: {path}")
        return None
    filename = os.path.basename(path)
    img = bpy.data.images.get(filename)
    if not img:
        img = bpy.data.images.load(path)
    print(f"Loaded image: {path}")
    return img

def ensure_material(obj, filt):
    if obj.type != "MESH":
        return None
    if obj.active_material.users > 1:
        obj.active_material = obj.active_material.copy()

    mat = obj.active_material
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf_node:
        bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf_node.location = (300, 300)

    tex_node = next((n for n in nodes if n.type == "TEX_IMAGE" and n.label == "BaseColor"), None)
    if not tex_node:
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.label = "BaseColor"
        tex_node.location = (0, 300)

    base_albedo = base_color_map.get(obj.name)
    img = None

    if filt == "Default":
        img_path = os.path.join(inputs_dir, base_albedo)
        img = load_image(img_path)
    else:
        name, ext = os.path.splitext(base_albedo)
        filtered_path = os.path.join(outputs_dir, f"{name}_{filt}.png")
        img = load_image(filtered_path)
        if not img:
            img_path = os.path.join(inputs_dir, base_albedo)
            img = load_image(img_path)

    if img:
        tex_node.image = img
        print(f"Applied BaseColor for {obj.name}: {img.filepath}")

    if not bsdf_node.inputs["Base Color"].is_linked:
        try:
            links.new(tex_node.outputs["Color"], bsdf_node.inputs["Base Color"])
        except:
            pass

    return bsdf_node, nodes, links

def apply_normal_map(obj, normal_base_name, filt):
    data = ensure_material(obj, filt)
    if not data:
        return

    bsdf_node, nodes, links = data

    if filt == "Default":
        normal_path = os.path.join(inputs_dir, f"{normal_base_name}.png")
    else:
        normal_path = os.path.join(outputs_dir, f"{normal_base_name}_{filt}.png")

    normal_img = load_image(normal_path)
    if not normal_img:
        print(f"Missing normal map: {normal_path}")
        return

    normal_node = next((n for n in nodes if n.type == "NORMAL_MAP"), None)
    if not normal_node:
        normal_node = nodes.new("ShaderNodeNormalMap")
        normal_node.location = (0, 0)
        normal_node.space = "OBJECT"

    tex_node = next((n for n in nodes if n.type == "TEX_IMAGE" and n.label == "NormalMap"), None)
    if not tex_node:
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.label = "NormalMap"
        tex_node.location = (-300, 0)

    tex_node.image = normal_img
    tex_node.image.colorspace_settings.name = "Non-Color"

    print(f"Applied NormalMap for {obj.name}: {normal_img.filepath}")

    for l in list(links):
        if l.to_node == bsdf_node and l.to_socket.name == "Normal":
            try:
                links.remove(l)
            except:
                pass

    links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])
    links.new(normal_node.outputs["Normal"], bsdf_node.inputs["Normal"])

def rotate_object_constant(obj, start_frame, end_frame, axis="Z"):
    if obj is None or obj.type != "MESH":
        return

    if obj.animation_data and obj.animation_data.action:
        obj.animation_data_clear()

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (0, 0, 0)
    obj.keyframe_insert("rotation_euler", frame=start_frame)

    rot = [0, 0, 0]
    if axis == "X": rot[0] = 2 * math.pi
    if axis == "Y": rot[1] = 2 * math.pi
    if axis == "Z": rot[2] = 2 * math.pi

    obj.rotation_euler = rot
    obj.keyframe_insert("rotation_euler", frame=end_frame)

    action = obj.animation_data.action
    for fc in action.fcurves:
        if fc.data_path == "rotation_euler":
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

def render_png(output_path):
    start = time.time()
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.frame_set(bpy.context.scene.frame_start)
    bpy.ops.render.render(write_still=True)
    elapsed = time.time() - start
    print(f"PNG saved: {output_path} (Time: {elapsed:.2f}s)")

def render_mp4(output_path):
    start = time.time()
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(animation=True)
    elapsed = time.time() - start
    print(f"MP4 saved: {output_path} (Time: {elapsed:.2f}s)")

frame_start = 1
frame_end = 120

bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end

for filt in filters:
    print(f"\n===== FILTER: {filt} =====")

    for obj_name, normal_base in object_map.items():
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            print(f"Missing object: {obj_name}")
            continue

        apply_normal_map(obj, normal_base, filt)
        rotate_object_constant(obj, frame_start, frame_end, axis="Z")

    png_path = os.path.join(outputs_dir, f"{filt}.png")
    render_png(png_path)

    mp4_path = os.path.join(outputs_dir, f"{filt}.mp4")
    render_mp4(mp4_path)
