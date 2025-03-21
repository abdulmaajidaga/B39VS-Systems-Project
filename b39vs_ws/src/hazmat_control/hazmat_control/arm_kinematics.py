import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the arm's link lengths
L1 = 0  # Length of link 1 (from base to second joint)
L2 = 1.0  # Length of link 2 (from second to third joint)
L3 = 1.0  # Length of link 3 (from third to end-effector)

# Define joint limits (in radians)
joint_limits = [
    [-np.pi, np.pi],  # Joint 1 (base rotation) limits
    [-np.pi, np.pi],  # Joint 2 (tilt) limits
    [-np.pi, np.pi],  # Joint 3 (tilt) limits
]

def forward_kinematics(theta1, theta2, theta3):
    """
    Compute the end-effector position in 3D using forward kinematics for a 3-DOF arm.
    """
    # Base rotation (around z-axis)
    x0, y0, z0 = 0, 0, 0

    # First joint (base rotation around z-axis)
    x1 = L1 * np.cos(theta1)
    y1 = L1 * np.sin(theta1)
    z1 = 0

    # Second joint (tilt around x-axis)
    x2 = x1 + L2 * np.cos(theta1) * np.cos(theta2)
    y2 = y1 + L2 * np.sin(theta1) * np.cos(theta2)
    z2 = z1 + L2 * np.sin(theta2)

    # Third joint (tilt along the previous link)
    x3 = x2 + L3 * np.cos(theta1) * np.cos(theta2 + theta3)
    y3 = y2 + L3 * np.sin(theta1) * np.cos(theta2 + theta3)
    z3 = z2 + L3 * np.sin(theta2 + theta3)

    return np.array([x3, y3, z3])

def inverse_kinematics(target_pos, initial_angles, max_iter=1000, tolerance=1e-5, learning_rate=0.1):
    """
    Perform inverse kinematics in 3D using gradient descent for a 3-DOF arm.
    """
    theta = np.array(initial_angles)  # Initial guess for joint angles

    for i in range(max_iter):
        # Compute current end-effector position
        current_pos = forward_kinematics(*theta)

        # Compute error
        error = target_pos - current_pos

        # Check if the error is within tolerance
        if np.linalg.norm(error) < tolerance:
            print(f"Converged after {i} iterations.")
            return theta

        # Compute Jacobian (numerical approximation)
        J = np.zeros((3, 3))
        delta = 1e-6
        for j in range(3):
            theta_perturbed = theta.copy()
            theta_perturbed[j] += delta
            pos_perturbed = forward_kinematics(*theta_perturbed)
            J[:, j] = (pos_perturbed - current_pos) / delta

        # Update joint angles using gradient descent
        theta += learning_rate * np.dot(J.T, error)

        # Apply joint limits
        for j in range(3):
            theta[j] = np.clip(theta[j], joint_limits[j][0], joint_limits[j][1])

    print("Warning: Max iterations reached.")
    return theta

def plot_arm_3d(theta1, theta2, theta3, target_pos):
    """
    Plot the 3-DOF arm configuration in 3D.
    """
    # Compute joint positions
    x0, y0, z0 = 0, 0, 0
    x1 = L1 * np.cos(theta1)
    y1 = L1 * np.sin(theta1)
    z1 = 0

    x2 = x1 + L2 * np.cos(theta1) * np.cos(theta2)
    y2 = y1 + L2 * np.sin(theta1) * np.cos(theta2)
    z2 = z1 + L2 * np.sin(theta2)

    x3 = x2 + L3 * np.cos(theta1) * np.cos(theta2 + theta3)
    y3 = y2 + L3 * np.sin(theta1) * np.cos(theta2 + theta3)
    z3 = z2 + L3 * np.sin(theta2 + theta3)

    # Create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the arm (with individual link colors)
    ax.plot([x0, x1], [y0, y1], [z0, z1], 'b-', label="Link 1", linewidth=3)  # Link 1 in blue
    ax.plot([x1, x2], [y1, y2], [z1, z2], 'g-', label="Link 2", linewidth=3)  # Link 2 in green
    ax.plot([x2, x3], [y2, y3], [z2, z3], 'r-', label="Link 3", linewidth=3)  # Link 3 in red

    # Plot the joints
    ax.plot([x0, x1, x2, x3], [y0, y1, y2, y3], [z0, z1, z2, z3], 'ko-', markersize=8)  # Joints in black

    # Plot the target position
    ax.scatter(target_pos[0], target_pos[1], target_pos[2], c='r', marker='x', s=100, label="Target Position")

    # Plot settings
    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-3, 3])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    plt.title("3-DOF Arm Configuration in 3D")
    plt.show()


# Example usage
target_position = np.array([1.0, 1.0, 1.0])  # Desired end-effector position in 3D
initial_angles = np.array([0.0, 0.0, 0.0])  # Initial joint angles

# Compute inverse kinematics
joint_angles = inverse_kinematics(target_position, initial_angles)
print("Computed joint angles (radians):", joint_angles)
print("End-effector position:", forward_kinematics(*joint_angles))

# Visualize the arm configuration in 3D
plot_arm_3d(*joint_angles, target_position)
