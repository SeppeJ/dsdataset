import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import sys
import os
import cv2
import bpycv
import bmesh
from mathutils import Matrix, Vector
import numpy as np
import json

VIEWS = 4

def create_dataset(RESOLUTION, VIEWS):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.render.image_settings.file_format = 'PNG' 
    bpy.data.scenes['Scene'].render.film_transparent = True
    bpy.data.scenes['Scene'].render.resolution_x = RESOLUTION
    bpy.data.scenes['Scene'].render.resolution_y = RESOLUTION
    bpy.data.scenes['Scene'].render.image_settings.color_depth = '8'
    
    cams = bpy.data.collections['Cameras'].all_objects
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    index_shapes = enumerate(bpy.data.collections['Objects'].all_objects)

    for index, shape in index_shapes:
        if(shape.type != "MESH"):
            continue
        shape["inst_id"] = index
        transforms_json = {}
        transforms_json["frames"] = []
        for indexcam, cam in enumerate(cams):
            bpy.data.scenes['Scene'].camera = cam
            frame_json = {}
            image_name = "r_" + str(indexcam) + ".png"
            image_path = os.path.join(directory, 'dsdataset', str(VIEWS), str(RESOLUTION), shape.name)
            if not os.path.exists(image_path):
                os.makedirs(image_path)
            frame_json["file_path"] =  image_name[:-4]
            frame_json["transform_matrix"] = listify_matrix(cam.matrix_world)
            camera_json = {}
            camera_json["angle_x"] = cam.data.angle_x
            camera_json["angle_y"] = cam.data.angle_y
            camera_json["shift_x"] = cam.data.shift_x
            camera_json["shift_y"] = cam.data.shift_y
            camera_json['sensor_height'] = cam.data.sensor_height
            camera_json['sensor_width'] = cam.data.sensor_width
            camera_json['sensor_fit'] = cam.data.sensor_fit
            frame_json["camera"] = camera_json
            transforms_json["frames"].append(frame_json)
            render_view(cam, os.path.join(image_path, image_name))
        transforms_json_path = os.path.join(directory, 'dsdataset', str(VIEWS), str(RESOLUTION), shape.name, "transforms.json")
        with open(transforms_json_path, 'w') as json_file: 
            json.dump(transforms_json, json_file)
            

def render_view(cam, image_path):
    result = bpycv.render_data()
    rgb_image = result["image"][..., ::-1]
    mask = result["inst"]
    transparent = np.where(mask==0)
    visible = np.where(mask!=0)
    mask[transparent] = 0
    mask[visible] = 255
    rgba_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2RGBA)
    rgba_image[:, :, 3] = mask
    cv2.imwrite(image_path, rgba_image)
    

def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list

def calculate_object_volume(obj):
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(obj.matrix_world)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    volume = 0
    for f in bm.faces:
        v1 = f.verts[0].co
        v2 = f.verts[1].co
        v3 = f.verts[2].co
        volume += v1.dot(v2.cross(v3)) / 6
    bm.free()
    return volume

if __name__ == "__main__":
    for RESOLUTION in [32, 64, 128, 256, 512]:
        create_dataset(RESOLUTION, VIEWS)
        
for shape in bpy.data.collections['Objects'].all_objects:
     if(shape.type != "MESH"):
         continue
     print(shape)
     print(calculate_object_volume(shape))