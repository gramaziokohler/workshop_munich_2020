## Build:
#  docker build --rm -f Dockerfile -t gramaziokohler/ros-um-kr60-planner .
#
# Usage:
#  docker pull gramaziokohler/ros-um-kr60-planner

FROM gramaziokohler/ros-base:19.11
LABEL maintainer "Gonzalo Casas <casas@arch.ethz.ch>"

SHELL ["/bin/bash","-c"]

# Install packages
RUN apt-get update && apt-get install -y \
    # ROS MoveIt
    ros-${ROS_DISTRO}-moveit \
    --no-install-recommends \
    # Clear apt-cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

ENV CATKIN_WS=/root/catkin_ws
RUN mkdir -p $CATKIN_WS/src

# Add robot packages to local catkin workspace
RUN echo "Building KR60 Planner for ROS" \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    # Update apt-get because its cache is always cleared after installs to keep image size down
    && apt-get update \
    # Kuka KR60 UM workshop package
    && git clone https://github.com/gramaziokohler/workshop_michigan.git /root/workshop_michigan \
    && ln -s /root/workshop_michigan/kuka_kr60/* $CATKIN_WS/src/ \
    # Install dependencies
    && cd $CATKIN_WS \
    && rosdep install -y --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} \
    # Build catkin workspace
    && catkin_make
