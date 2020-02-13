#!/usr/bin/env python
#
# Copyright 2019 DFKI GmbH.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.
from copy import deepcopy
import numpy as np
from ...graphics.geometry.mesh import Mesh
from .component_base import ComponentBase
from ...graphics import materials
from ...graphics import renderer
from ...graphics.material_manager import MaterialManager

SKELETON_NODE_TYPE_ROOT = 0
SKELETON_NODE_TYPE_JOINT = 1
SKELETON_NODE_TYPE_END_SITE = 2
MAX_BONES = 150



class AnimatedMeshComponentLegacy(ComponentBase):
    def __init__(self, scene_object, position, mesh_list, skeleton_def):
        ComponentBase.__init__(self, scene_object)
        self._scene_object = scene_object
        self.skeleton = scene_object._components["animation_controller"]._visualization
        self.meshes = []
        material_manager = MaterialManager()
        for m_desc in mesh_list:
            if "material" in m_desc and "Kd" in list(m_desc["material"].keys()):
                material = material_manager.get(m_desc["texture"])
                if material is None:
                    material = materials.TextureMaterial.from_image(m_desc["material"])
                    material_manager.set(m_desc["texture"], material)
                print("reuse material", m_desc["texture"])
                self.meshes.append(renderer.TexturedMeshRenderer(position, m_desc, material))
            else:
                print("create untextured mesh")
                self.meshes.append(renderer.ColoredMeshRenderer(position, m_desc))
        self.inv_bind_poses = []
        for name in skeleton_def["animated_joints"]:
             inv_bind_pose = skeleton_def["nodes"][name]["inv_bind_pose"]
             self.inv_bind_poses.append(inv_bind_pose)
        self.vertex_weight_info = [] # store for each vertex a list of tuples with bone and weights
        for idx, m in enumerate(mesh_list):
            self.vertex_weight_info.append(mesh_list[idx]["weights"])
        self.updated = False


    def update(self, dt):
        if not self.updated:
            for m_idx, m in enumerate(self.meshes):
                new_vertices = self.updateVertices(m_idx, m)
                m.updateMesh(new_vertices)
            self.updated = True

    def updateVertices(self, m_idx, mesh):
        """
        Calculates the new position of each vertex based on the lastGlobalTransformationMatrix of each joint controller
        * vertexList : np.ndarray
          An array in which each element contains the position and the normal of a vertex as an array with six elements.
        """
        new_mesh = deepcopy(mesh.vertexList)
        for vi in range(len(new_mesh)):
            global_v = np.array(new_mesh[vi][:3].tolist() + [1])
            global_n = np.array(new_mesh[vi][3:6])
            tmp_v = np.array([0.0, 0.0, 0.0])
            tmp_n = np.array([0.0, 0.0, 0.0])
            bone_weight_list = self.vertex_weight_info[m_idx][vi]# starts at zero for each mesh
            for idx in range(4):
                b_idx = bone_weight_list[0][idx]
                w = bone_weight_list[1][idx]
                if w <= 0:
                    continue
                transform = np.dot(self.skeleton.matrices[b_idx], self.inv_bind_poses[b_idx])

                t_pos = np.dot(transform, global_v)  # transform position
                t_norm = np.dot(transform[:3, :3], global_n)  # rotate normal
                tmp_v += w * t_pos[:3]
                tmp_n += w * t_norm
            new_mesh[vi][:6] = tmp_v.tolist() + tmp_n.tolist()
        return new_mesh

    def draw(self, modelMatrix, viewMatrix, projectionMatrix, lightSources):
        for m in self.meshes:
            m.draw(modelMatrix, viewMatrix, projectionMatrix, lightSources)



RENDER_MODE_NONE = 0
RENDER_MODE_STANDARD = 1
RENDER_MODE_NORMAL_MAP = 2
RENDER_MODES = [RENDER_MODE_NONE, RENDER_MODE_STANDARD, RENDER_MODE_NORMAL_MAP]


class AnimatedMeshComponent(ComponentBase):
    def __init__(self, scene_object, mesh_list, skeleton_def, animation_source="animation_controller", scale=1):
        ComponentBase.__init__(self, scene_object)
        self._scene_object = scene_object
        self.anim_controller = scene_object._components[animation_source]
        self.render_mode = RENDER_MODE_STANDARD
        self.meshes = []

        material_manager = MaterialManager()

        for m_desc in mesh_list:
            if "material" in m_desc and "Kd" in list(m_desc["material"].keys()):
                texture_name = m_desc["texture"]
                if texture_name is not None and texture_name.endswith(b'Hair_texture_big.png'):
                    continue
                material = material_manager.get(m_desc["texture"])
                if material is None:
                    material = materials.TextureMaterial.from_image(m_desc["material"])
                    material_manager.set(m_desc["texture"], material)
                print("reuse material", m_desc["texture"])
                geom = Mesh.build_legacy_animated_mesh(m_desc, material)
                if geom is not None:
                    self.meshes.append(geom)
        self.inv_bind_poses = []
        for idx, name in enumerate(skeleton_def["animated_joints"]):
             print(idx, name)
             inv_bind_pose = skeleton_def["nodes"][name]["inv_bind_pose"]
             self.inv_bind_poses.append(inv_bind_pose)
        self.vertex_weight_info = [] # store for each vertex a list of tuples with bone id and weights
        for idx, m in enumerate(mesh_list):
            self.vertex_weight_info.append(mesh_list[idx]["weights"])
        self.scale_mesh(scale)
        print("number of matrices", len(self.inv_bind_poses))

    def update(self, dt):
        return

    def get_bone_matrices(self):
        matrices = self.anim_controller.get_bone_matrices()
        bone_matrices = []
        for idx in range(len(self.inv_bind_poses)):
            m = np.dot(matrices[idx], self.inv_bind_poses[idx])

            bone_matrices.append(m)
        return np.array(bone_matrices)

    def scale_mesh(self, scale_factor):
        for m in self.meshes:
            m.scale(scale_factor)
        for idx, m in enumerate(self.inv_bind_poses):
            self.inv_bind_poses[idx][:3, 3] *= scale_factor

