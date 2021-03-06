# Workshop TU Munich 5., 6., and 20.11.2020

This workshop is about robotic assembly using the COMPAS framework.

## Overview

* COMPAS 101
* COMPAS FAB Intro
* Kinematics and path planning
* Attach/detach tools
* Pick and Place planning
* Brick assembly
* Robot control overview

## Examples

### Day 1

* **Slides**: [session 1](https://docs.google.com/presentation/d/1nexXDZrQxwgEsNyjcaFsndLgY3z8m6igXAWk9GWiQAg/edit?usp=sharing)
* **Documentation**:
  * [COMPAS API Reference](https://compas.dev/compas/latest/api.html)
  * [COMPAS FAB API Reference](https://gramaziokohler.github.io/compas_fab/latest/reference.html)

#### Robotic fundamentals

* `Frame` examples:
  * [Several ways to construct a `Frame`](examples/001_several_ways_to_construct_frame.py)
  * [`Point` in `Frame`](examples/002_point_in_frame.py)
  * [`Frame` in `Frame`](examples/003_frame_in_frame.py)
  * [Bring a box from the world coordinate frame into another coordinate frame](examples/004_box_from_the_world_to_local.py)
  * [Use artists to draw the box in Rhino](examples/005_box_from_the_world_to_local_rhino.py)
* `Transformation` examples:
  * [Several ways to construct a `Transformation`](examples/006_examples_transformation.py)
  * [Inverse transformation](examples/007_inverse_transformation.py)
  * [Pre-multiply transformations](examples/008_premultiply_transformations.py)
  * [Pre- vs. post-multiplication](examples/009_pre_vs_post_multiplication.py)
  * [Decompose transformation](examples/010_decompose_transformation.py)
  * [Transform `Point` and `Vector`](examples/011_transform_point_and_vector.py)
  * [Transformation of multiple points](examples/012_transform_multiple.py)
  * [Change-basis transformation vs. transformation between frames](examples/013_change_basis_vs_between_frames.py)
  * [Bring a box from the world coordinate frame into another coordinate frame](examples/014_box_from_the_world_to_local.py)
  * [Use artists to draw the box in Rhino](examples/015_box_from_the_world_to_local_rhino.py)
* `Rotation` examples:
  * [Several ways to construct a `Rotation`](examples/016_several_ways_to_construct_rotation.py)
  * [Different Robot vendors use different conventions to describe TCP orientation](examples/017_robot_tcp_orientations.py)
  * [Euler angles example](examples/018_euler_angles.py)
  * [Axis-angle example](examples/019_axis_angle.py)
  * [Unit Quaternion example](examples/020_quaternion.py)

#### Robot model and ROS 1

* [Docker configuration to launch ROS & MoveIt](docker/)
* Open MoveIt! in your browser:
  * `http://localhost:8080/vnc.html?resize=scale&autoconnect=true`
* Basic examples:
  * [Programmatically define a robot](examples/021_define_model.py)
  * [Load robots from Github](examples/022_robot_from_github.py)
  * [Load robots from ROS](examples/023_robot_from_ros.py)
  * [Visualize robots in Rhino](examples/024_robot_artist_rhino.py)
  * [Visualize robots in Grasshopper](examples/025_robot_artist_grasshopper.ghx)
  * [Build your own robot](examples/026_build_your_own_robot.py)
* Basic ROS examples:
  * [Verify connection](examples/027_check_connection.py)
  * The canonical example of ROS: chatter nodes
    * [Talker node](examples/028_ros_hello_world_talker.py)
    * [Listener node](examples/029_ros_hello_world_listener.py)

### Day 2

* **Slides**:  [session 2](https://docs.google.com/presentation/d/1Xbnb7wsjBr_FTUruj6bN0ltFRs4hd55l4udoDYYLtlA/edit?usp=sharing)
* **Documentation**:
  * [COMPAS API Reference](https://compas.dev/compas/latest/api.html)
  * [COMPAS FAB API Reference](https://gramaziokohler.github.io/compas_fab/latest/reference.html)

#### RPC: Remote Procedure Call

* Examples of RPC calls:
  * [Simple numpy example](examples/060_rcp_simple_example.py)
  * [Custom function example](examples/061_rcp_custom_functions.py)

#### Robot model and ROS 2

* Examples of ROS & MoveIt planning with UR10e:
  * [Forward Kinematics](examples/030_forward_kinematics_ros_loader.py)
  * [Inverse Kinematics](examples/031_inverse_kinematics_ros_loader.py)
  * [Cartesian motion planning](examples/032_plan_cartesian_motion_ros_loader.py)
  * [Free space motion planning](examples/033_plan_motion_ros_loader.py)
  * Planning scene management:
    * [Add objects to the scene](examples/034_add_collision_mesh.py)
    * [Append nested objects to the scene](examples/035_append_collision_meshes.py)
    * [Remove objects from the scene](examples/036_remove_collision_mesh.py)
* [Grasshopper Playground](examples/038_robot_playground.ghx)

#### Path planning and assembly processes

* [Docker configuration to launch ROS & MoveIt](docker/)
* [Assembly Playground](examples/050_robot_assembly.ghx)
* Attaching gripper/tool:
  * [Attach tool to last link of the robot](examples/041_attach_tool.py)
  * [Plan cartesian motion with attached tool](examples/042_plan_cartesian_motion_with_attached_tool.py)
* Assembly elements (e.g. bricks):
  * [Add assembly element to planning scene](examples/043_create_element_and_add_to_planning_scene.py)
  * [Attach assembly element to gripper](examples/044_add_element_as_attached_collision_object.py)
* Assembly examples:
  * [Pick and place example](examples/045_pick_and_place.py)
  * [Assembly example](examples/046_assembly_example.py)
  * [Plan assembly paths](examples/047_plan_paths_assembly.py)

### Day 3

* Assembly examples with real robot:
  * [Assembly Playground](examples/050_robot_assembly.ghx)
  * [Send assembly tasks to robot](examples/051_send_assembly_task.py)
  * [Subscribe to robot updates](examples/052_subscribe_joint_states.py)
  * [Visualize robot updates in Grasshopper](examples/052_subscribe_joint_states_visualization.ghx)
* Robot control:
  * [Control services](control/control_services.py)
  * [Joint State Publisher](control/joint_state_publisher.py)

![Diagram](robot-diagram.png)
## Requirements

* Minimum OS: Windows 10 Pro or Mac OS Sierra 10.12
* [Anaconda 3](https://www.anaconda.com/distribution/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop) Docker Toolbox would also work but it's a bit more annoying. After installation on Windows, it is required to enable "Virtualization" on the BIOS of the computer.
* [Rhino 6 & Grasshopper](https://www.rhino3d.com/download)
* [Visual Studio Code](https://code.visualstudio.com/): Any python editor works, but we recommend VS Code + extensions [as mentioned in our docs](https://gramaziokohler.github.io/compas_fab/latest/getting_started.html#working-in-visual-studio-code-1)

## Installation

We use `conda` to make sure we have clean, isolated environment for dependencies.

First time using `conda`? Make sure you run this at least once:

    (base) conda config --add channels conda-forge

Create a new conda environment:

**Windows**

    (base) conda create -n tum20 python=3.8 compas_fab=0.13 --yes
    (base) conda activate tum20

**Mac**

    (base) conda create -n tum20 python=3.8 compas_fab=0.13 python.app --yes
    (base) conda activate tum20

### Install TUM assembly information model library

    (tum20) conda install git
    (tum20) python -m pip install git+https://github.com/augmentedfabricationlab/assembly_information_model@compas_upgrade#egg=assembly_information_model
    (tum20) python -m compas_rhino.install -p assembly_information_model

### Verify installation

    (tum20) pip show compas_fab
    Name: compas-fab
    Version: 0.13.1
    Summary: Robotic fabrication package for the COMPAS Framework
    ...

### Install on Rhino

    (tum20) python -m compas_rhino.install

NOTE: This installs to Rhino 6.0, use `-v 5.0` if needed.
