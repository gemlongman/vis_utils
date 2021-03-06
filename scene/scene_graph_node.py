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
import numpy as np
from transformations import euler_matrix, quaternion_matrix
from ..graphics import utils
from .utils import get_global_id


class SceneGraphNode(object):
    def __init__(self, parentNode=None):
        self.scene = None
        self.body = None
        self.parentNode = parentNode
        self.transformation = np.eye(4)
        self.scale_matrix = np.eye(4)
        self.children = []
        self.is_root = False
        self.node_id = get_global_id()  # Gives every object in the scene a unique id to allow interaction

    def addChildNode(self, node):
        self.children.append(node)

    def removeChildNode(self, node_id):
        for node in self.children:
            if node.node_id == node_id:
                node.cleanup()
                self.children.remove(node)
            else:
                node.removeChildNode(node_id)

    def getSceneNode(self, node_id):
        #print "search for", node_id,"in",self.node_id,self.children
        for c in self.children:
            #print "check", node_id,c.node_id
            if c.node_id == node_id:
                return c
            else:
                temp = c.getSceneNode(node_id)
                if temp is not None:
                    return temp
        return None

    def getChildren(self):
        children = self.children
        for c in self.children:
            children += c.getChildren()
        return children

    def getParentTransformation(self):
        if self.parentNode is not None and not self.parentNode.is_root:
            return self.parentNode.getGlobalTransformation()
        else:
            return np.eye(4)

    def getGlobalTransformation(self):
        transformation = self.transformation
        node = self.parentNode
        while node is not None and not node.is_root:
            transformation = np.dot(transformation, node.transformation)
            node = node.parentNode
        return transformation

    def setRelativePosition(self, position):
        self.transformation = np.dot(self.getParentTransformation(), utils.get_translation_matrix(position))

    def setPosition(self, position):
        self.transformation = np.dot(np.linalg.inv(self.getParentTransformation()), utils.get_translation_matrix(position))

    def setOrientation(self, x, y, z):
        local = euler_matrix(x, y, z)
        local[3, :3] = self.transformation[3, :3]
        self.transformation = np.dot(np.linalg.inv(self.getParentTransformation()), local)

    def setQuaternion(self, q):
        local = quaternion_matrix(q)
        local[3, :3] = self.transformation[3, :3]
        self.transformation = np.dot(np.linalg.inv(self.getParentTransformation()), local)

    def getPosition(self):
        transformation = self.getGlobalTransformation()
        return transformation[3, :3] #* self.get_scale()

    def set_scale(self, scale):
        #self.scale_matrix[0][0] = scale
        #self.scale_matrix[1][1] = scale
        #self.scale_matrix[2][2] = scale
        self.transformation[:3,:3] *= np.eye(3) * scale

    def get_scale(self):
        return self.scale_matrix[0][0]

    def cleanup(self):
        pass

    def translate(self, v):
        self.transformation[3,:3] += v

    def get_scene_node_by_name(self, node_name):
        #print "search for", node_id,"in",self.node_id,self.children
        for c in self.children:
            if c.name == node_name:
                return c
            else:
                temp = c.get_scene_node_by_name(node_name)
                if temp is not None:
                    return temp
        return None
