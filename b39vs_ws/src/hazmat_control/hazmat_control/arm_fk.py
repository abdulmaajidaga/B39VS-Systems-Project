import PyKDL as kdl

def main():
    # Define the kinematic chain
    chain = kdl.Chain()

    # Add segments (replace lengths with actual lengths of your robot arm links)
    chain.addSegment(kdl.Segment(kdl.Joint(kdl.Joint.RotZ), kdl.Frame(kdl.Vector(0.0, 0.0, 0.5))))
    chain.addSegment(kdl.Segment(kdl.Joint(kdl.Joint.RotZ), kdl.Frame(kdl.Vector(0.0, 0.0, 0.7))))
    chain.addSegment(kdl.Segment(kdl.Joint(kdl.Joint.RotZ), kdl.Frame(kdl.Vector(0.0, 0.0, 0.6))))
    chain.addSegment(kdl.Segment(kdl.Joint(kdl.Joint.RotZ), kdl.Frame(kdl.Vector(0.0, 0.0, 0.4))))
    
    # Create a solver for forward kinematics
    fk_solver = kdl.ChainFkSolverPos_recursive(chain)

    # Define joint positions (replace with your arm's joint angles)
    joint_positions = kdl.JntArray(chain.getNrOfJoints())
    joint_positions[0] = 0.5  # First joint angle
    joint_positions[1] = 1.0  # Second joint angle
    joint_positions[2] = -0.5 # Third joint angle
    joint_positions[3] = 0.2  # Fourth joint angle

    # Define a frame to store the result
    end_effector_pose = kdl.Frame()

    # Perform the forward kinematics
    result = fk_solver.JntToCart(joint_positions, end_effector_pose)

    if result >= 0:
        print("End effector pose: ")
        print(end_effector_pose)
    else:
        print("Error: Could not calculate forward kinematics.")

if __name__ == '__main__':
    main()
