# Build:
#  docker build --rm -f Dockerfile -t gramaziokohler/ros-tum-assembly-demo .
#
# Usage:
#  docker pull gramaziokohler/ros-tum-assembly-demo

FROM gramaziokohler/ros-ur-planner
LABEL maintainer "Gonzalo Casas <casas@arch.ethz.ch>"

ENV CATKIN_WS=/root/catkin_ws

RUN echo "Adding Assembly Task messages" \
    && source /opt/ros/${ROS_DISTRO}/setup.bash \
    # Update apt-get because its cache is always cleared after installs to keep image size down
    && apt-get update && apt-get -y upgrade \
    # UR packages
    && git clone https://github.com/gonzalocasas/workshop_tum20_msgs.git \
    # Install dependencies
    && cd $CATKIN_WS \
    && rosdep install -y --from-paths . --ignore-src --rosdistro ${ROS_DISTRO} \
    # Build catkin workspace
    && catkin_make \
    # Clear apt-cache to reduce image size
    && rm -rf /var/lib/apt/lists/*
