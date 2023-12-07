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

def create_dataset():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.render.image_settings.file_format = 'PNG' 
    cams = bpy.data.collections['Cameras'].all_objects
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    index_shapes = enumerate(bpy.data.collections['Objects'].all_objects)

    for index, shape in index_shapes:
        transforms_json = {}
        transforms_json["frames"] = []
        for indexcam, cam in enumerate(cams):
            frame_json = {}
            image_name = "r_" + str(indexcam) + ".png"
            image_path = os.path.join(directory, 'dsdataset', shape.name)
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
        transforms_json_path = os.path.join(directory, 'dsdataset', shape.name, "transforms.json")
        with open(transforms_json_path, 'w') as json_file: 
            json.dump(transforms_json, json_file)
            


def render_view(cam, image_path):
    bpy.data.scenes['Scene'].camera = cam
    result = bpycv.render_data()
#    image_path = os.path.join(directory, "r_" + str(indexcam) + ".png")
#    with open(os.path.join(directory,'test'),'w') as file_object:
#         file_object.write("%s" % image_path)
#    image_path = os.path.join(directory, shapename+ ".png")
#    depth_path = os.path.join(directory, 'dataset', shapename,"/d_" , str(indexcam) + ".png")
#    segmentation_path = os.path.join(directory, 'dataset', shapename,"/s_" , str(indexcam) + ".png")
#    combined_path = os.path.join(directory, 'dataset', shapename,"/c_" , str(indexcam) + ".png")
    cv2.imwrite(image_path, result["image"][..., ::-1])
#    cv2.imwrite(depth_path, np.uint16(result["depth"]*1000))
#    cv2.imwrite(segmentation_path,  np.uint16(result["inst"]))
#    cv2.imwrite(combined_path, result.vis()[..., ::-1])

def listify_matrix(matrix):
    matrix_list = []
    for row in matrix:
        matrix_list.append(list(row))
    return matrix_list

if __name__ == "__main__":
    create_dataset()
