Hazmat, an indoor waste transportation and disposal robot.

## Setup

To clone the repo, ensure to also include the submodules:

```bash
# Replace the url with https version if you don't have repo access
git clone --recurse-submodules git@github.com:abdulmaajidaga/B39VS-Systems-Project.git
```

If you've already cloned the repo without the submodules, then run 

```bash
git submodule update --init
```

To build the ROS2 workspace, install the following dependencies:

- depthai
- pyserial

You can install the above on Ubuntu or related distros using:

```bash
sudo apt install python3-serial ros-${ROS_DISTRO}-depthai
```

To ensure depthai drivers can access the OAK-D camera on the USB port, update your udev rules as such:

```bash
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Simulation

To start Unity's TCP connecter, first build and source the workspace (with submodules, see above). Then run the connector node

```bash
ros2 run ros_tcp_endpoint default_server_endpoint
```

To send wheel commands to the robot at 30Hz, use

```bash
ros2 topic pub /wheel_cmd hazmat_msgs/msg/MecanumCmd "{rear_right: 1.0, rear_left: 1.0, front_right: 1.0, front_left: 1.0}" -r 30
```

To send linear and angular velocity commands at the same, use

```bash
ros2 topic pub /hazmat/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0, y: 2.0}}" -r 30
```
