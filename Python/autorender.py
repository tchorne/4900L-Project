import bpy
import os
import math

blend_dir = os.path.dirname(bpy.data.filepath)
project_dir = os.path.dirname(blend_dir)
outputs_dir = os.path.join(project_dir, "Python", "Outputs")
os.makedirs(outputs_dir, exist_ok=True)

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


filters = ["SLIC", "LayeredPaint", "Kuwahara"]


def load_image(filename):
    path = os.path.join(outputs_dir, filename)
    if not os.path.exists(path):
        print(f"❌ Image not found: {path}")
        return None
    img = bpy.data.images.get(filename)
    if not img:
        img = bpy.data.images.load(path)
    return img

def ensure_material(obj, filt=None):
    if obj.type != "MESH":
        return None

    if obj.active_material.users > 1:
        obj.active_material = obj.active_material.copy()
    mat = obj.active_material
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Principled BSDF
    bsdf_node = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if not bsdf_node:
        bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf_node.location = (300, 300)

    # Base Color
    tex_node = next((n for n in nodes if n.type == "TEX_IMAGE" and n.label == "BaseColor"), None)
    if not tex_node:
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.label = "BaseColor"
        tex_node.location = (0, 300)

    base_albedo = base_color_map.get(obj.name)
    img = None
    if base_albedo and filt:
        name, ext = os.path.splitext(base_albedo)
        filtered_albedo = f"{name}_{filt}.png"
        img = load_image(filtered_albedo)
    if not img and base_albedo:
        img = load_image(base_albedo)
    if img:
        tex_node.image = img

    # Link base color
    if not bsdf_node.inputs["Base Color"].is_linked:
        try:
            links.new(tex_node.outputs["Color"], bsdf_node.inputs["Base Color"])
        except:
            pass

    return bsdf_node, nodes, links

def apply_normal_map(obj, normal_img, filt):
    data = ensure_material(obj, filt)
    if not data:
        return
    bsdf_node, nodes, links = data

    # Normal node
    normal_node = next((n for n in nodes if n.type == "NORMAL_MAP"), None)
    if not normal_node:
        normal_node = nodes.new("ShaderNodeNormalMap")
        normal_node.location = (0, 0)
        normal_node.space = "OBJECT"

    # Texture node
    tex_node = next((n for n in nodes if n.type == "TEX_IMAGE" and n.label == "NormalMap"), None)
    if not tex_node:
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.label = "NormalMap"
        tex_node.location = (-300, 0)

    tex_node.image = normal_img
    tex_node.image.colorspace_settings.name = "Non-Color"

    # Remove old normal links
    for l in list(links):
        if l.to_node == bsdf_node and l.to_socket.name == "Normal":
            try: links.remove(l)
            except ReferenceError: pass

    # Connect normal
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

    rot = list(obj.rotation_euler)
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
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.frame_set(bpy.context.scene.frame_start)
    bpy.ops.render.render(write_still=True)
    print(f"PNG saved: {output_path}")


def render_mp4(output_path):
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(animation=True)
    print(f"MP4 saved: {output_path}")


frame_start = 1
frame_end = 120
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end


for filt in filters:
    print(f"\n===== FILTER: {filt} =====")
    for obj_name, base_name in object_map.items():
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            print(f"Missing object: {obj_name}")
            continue

        normal_img = load_image(f"{base_name}_{filt}.png")
        if not normal_img:
            print(f"Missing normal map: {base_name}_{filt}.png")
            continue

        apply_normal_map(obj, normal_img, filt)
        rotate_object_constant(obj, frame_start, frame_end, axis="Z")

    # Render PNG preview 
    png_path = os.path.join(outputs_dir, f"{filt}.png")
    render_png(png_path)

    # Render MP4 animation
    mp4_path = os.path.join(outputs_dir, f"{filt}.mp4")
    render_mp4(mp4_path)
