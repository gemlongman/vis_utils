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
from .renderer.text_renderer import TextRenderer


class Console(object):
    def __init__(self, top_left, scale=1.0, z=-10):
        self.text_renderer = TextRenderer()

        self.top_left = np.array(top_left)
        self.min_pos = np.array(self.top_left[:])
        self.scale = scale
        self.z = z
        self.lines = []

    def reset(self):
        self.min_pos = np.array(self.top_left[:])

    def draw(self, orthographic_matrix, lines):
        for line in lines:
            ix, iy = self.text_renderer.draw(orthographic_matrix, self.min_pos, self.z, line, self.scale)
            self.min_pos[1] = iy

    def draw_lines(self, orthographic_matrix):
        self.min_pos = np.array(self.top_left[:])
        for line in self.lines:
            ix, iy = self.text_renderer.draw(orthographic_matrix, self.min_pos, self.z, line, self.scale)
            self.min_pos[1] = iy

    def set_lines(self, lines):
        self.lines = lines

    def add_line(self, line):
        self.lines.append(line)