# Visualization Utilities

Simple scene graph and OpenGL 3.3 renderer for data structures from [anim_utils](https://github.com/eherr/anim_utils.git)  
The code was developed as a side project for debugging purposes based on the following sources:  
http://www.glprogramming.com/  
https://learnopengl.com  
http://www.lighthouse3d.com/tutorials  
https://www.youtube.com/user/ThinMatrix  


Note: To use the library on Windows, please install the PyOpenGL wheel provided by Cristoph Gohlke which also contains the GLUT-DLLs:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl


## Example 

```python   
from vis_utils.glut_app import GLUTApp
from vis_utils.scene.task_manager import Task

def print_global_vars(dt, app):
    scene = app.scene
    lines = []
    for key in scene.global_vars:
        value = str(scene.global_vars[key])
        lines.append(key+": "+value)
    app.set_console_lines(lines)

    
def control_func(key, params):
    app, controller = params
    if key == str.encode(" "):
        controller.toggleAnimation()
    elif key == str.encode("l"):
        controller.loopAnimation = not controller.loopAnimation

    app.scene.global_vars["frame"] = controller.get_current_frame_idx()
    app.scene.global_vars["loop"] = controller.loopAnimation
    app.scene.global_vars["speed"] = controller.animationSpeed

def main(bvh_file):
    c_pose = dict()
    c_pose["zoom"] = -500
    c_pose["position"] = [0, 0, -50]
    c_pose["angles"] = (45, 200)
    app = GLUTApp(800, 600, title="bvh player",console_scale=0.4, camera_pose=c_pose)
    o = app.scene.object_builder.create_object_from_file("bvh", bvh_file)
    c = o._components["animation_controller"]
    app.keyboard_handler["control"] = (control_func, (app, c))
    
    app.scene.draw_task_manager.add("print", Task("print", print_global_vars, app))
    app.run()
main("example.bvh")


```

The library also supports the import of character meshes and skeletons from glb and fbx files. To enable the fbx support a custom [FBX SDK Wrapper](https://github.com/eherr/py_fbx_wrapper) has to be build and copied into the directory "vis_utils/io".


```python   

    app.scene.object_builder.create_object_from_file("glb", glb_file)
    app.scene.object_builder.create_object_from_file("fbx", fbx_file)

```


## Developer

Erik Herrmann (erik.herrmann at dfki.de)



## License
Copyright (c) 2019 DFKI GmbH.  
MIT License, see the LICENSE file.



