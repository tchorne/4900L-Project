import bpy
import os

# paths
blend_dir = os.path.dirname(bpy.data.filepath)
normal_map_path = os.path.join(blend_dir, "bowl_object_space_normal_map_FotoSketcher.jpg") # change to weherever the normal map is
output_path = os.path.join(blend_dir, "output_render.png")

# name of object in blender
target_object_name = "Cylinder" #change name depending on object name

# image loading
if not os.path.exists(normal_map_path):
    raise FileNotFoundError(f"Could not find {normal_map_path}")

img_name = os.path.basename(normal_map_path)
img = bpy.data.images.get(img_name)
if not img:
    img = bpy.data.images.load(normal_map_path)

# apply normal map to object
def apply_normal_map_to_object(obj, image):
    if obj.type != 'MESH' or not obj.active_material:
        print(f"Skipping {obj.name} (not a mesh or no material).")
        return

    # make a unique copy of the material so only this object changes
    if obj.active_material.users > 1:
        print(f"Duplicating material for {obj.name}")
        obj.active_material = obj.active_material.copy()

    mat = obj.active_material
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    tex_node = None
    normal_node = None
    bsdf = None

    # look for existing nodes by type (not just name)
    for n in nodes:
        if n.type == 'TEX_IMAGE':
            if n.image == image or "NormalMapTex" in n.name:
                tex_node = n
        elif n.type == 'NORMAL_MAP':
            normal_node = n
        elif n.type == 'BSDF_PRINCIPLED':
            bsdf = n

    # create missing nodes
    if not tex_node:
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.name = "NormalMapTex"
    tex_node.image = image
    tex_node.image.colorspace_settings.name = "Non-Color"

    if not normal_node:
        normal_node = nodes.new("ShaderNodeNormalMap")
        normal_node.name = "NormalMapNode"
    normal_node.space = 'OBJECT'  # object Space

    if not bsdf:
        print(f"No Principled BSDF found in {mat.name}")
        return

    # clean links
    # remove any links into the BSDF Normal input
    for link in list(links):
        if link.to_node == bsdf and link.to_socket.name == "Normal":
            links.remove(link)
    # remove any link into the NormalMapNode Color input
    for link in list(links):
        if link.to_node == normal_node and link.to_socket.name == "Color":
            links.remove(link)

    #link nodes
    links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])
    links.new(normal_node.outputs["Normal"], bsdf.inputs["Normal"])

    print(f"Applied normal map to: {obj.name} (material: {mat.name})")

# apply to target object
obj = bpy.data.objects.get(target_object_name)
if not obj:
    raise ValueError(f"Object '{target_object_name}' not found in the scene.")

apply_normal_map_to_object(obj, img)

#  render amd export
bpy.context.scene.render.filepath = output_path
bpy.ops.render.render(write_still=True)
print(f"Render complete: {output_path}")