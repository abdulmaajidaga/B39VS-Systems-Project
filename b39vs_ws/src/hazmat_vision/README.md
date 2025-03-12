Vision startup commands (in-order)


```
ros2 launch depthai_ros_driver camera.launch.py  pointcloud.enable:=true parent_frame:=camera_link
```

```
ros2 run cartographer_ros cartographer_occupancy_grid_node -resolution 0.05 -publish_period_sec 1.0
```

```
ros2 run cartographer_ros cartographer_node -configuration_directory ./b39vs_ws/src/hazmat_vision/ -configuration_basename carto_oak.lua --ros-args -r /points2:=/oak/points
```