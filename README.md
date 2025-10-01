# COMP 4900L - Computer Graphics
# Final Project
# Procedural Painterly Aesthetic via Processed Object Space Normal Maps

Thomas Horne, 101256754 \
Vincent Vogl, 101141514 \
Mohammad Danial Abbas, 101269146


# Timeline

**October 8**: 
- Have a Blender scene with at least 3 meshes - Vincent 
- Python script is ready to read and write images - Thomas

**October 15**: 
- Export a meshes Object Space normal map, modify it externally, and \
use it in Blender's shader editor to render a result - Danial
- Implement [SLIC](https://darshita1405.medium.com/superpixels-and-slic-6b2d8a6e4f08)
in the Python code - Thomas

**October 22**:
- Implement the pseudocode in the Hertzmann paper on page 22 - Thomas
- Attempt to create a Blender script that can load our normal maps from disk \
and render our scene into an output image in one click - Danial and/or Vincent
  - Seems like it's definitely possible, I prompted ChatGPT with `Is it possible to have some kind of script with Blender which can load in some images with specific names from disk, apply them as normal maps to specific shader nodes, and render an image and write it to disk` and it gave a response which looked pretty straightforward

**October 28**: 
- Finish interim report - Everyone