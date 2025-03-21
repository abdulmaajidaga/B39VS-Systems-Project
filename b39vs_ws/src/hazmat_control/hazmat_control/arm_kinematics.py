import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider

# Define the arm's link lengths
L1 = 0  # Length of link 1 (from base to second joint)
L2 = 1.0  # Length of link 2 (from second to third joint)
L3 = 1.0  # Length of link 3 (from third to end-effector)

# Define joint limits (in radians)
joint_limits = [
    [-np.pi, np.pi],  # Joint 1 (base rotation) limits
    [-np.pi, np.pi],  # Joint 2 (base tilt) limits
    [-np.pi, np.pi],  # Joint 3 (air joint) limits
]

def forward_kinematics(theta1, theta2, theta3):
    """Compute the end-effector position in 3D using forward kinematics."""
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

    return np.array([x3, y3, z3])

def inverse_kinematics(target_pos, initial_angles, max_iter=1000, tolerance=1e-5, learning_rate=0.1):
    """Perform inverse kinematics in 3D using gradient descent."""
    theta = np.array(initial_angles)

    for i in range(max_iter):
        current_pos = forward_kinematics(*theta)
        error = target_pos - current_pos

        if np.linalg.norm(error) < tolerance:
            return theta

        J = np.zeros((3, 3))
        delta = 1e-6
        for j in range(3):
            theta_perturbed = theta.copy()
            theta_perturbed[j] += delta
            pos_perturbed = forward_kinematics(*theta_perturbed)
            J[:, j] = (pos_perturbed - current_pos) / delta

        theta += learning_rate * np.dot(J.T, error)
        for j in range(3):
            theta[j] = np.clip(theta[j], joint_limits[j][0], joint_limits[j][1])

    return theta

def plot_arm_3d(ax, theta1, theta2, theta3, target_pos):
    """Update the plot with the current arm configuration."""
    ax.cla()

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

    ax.plot([x0, x1], [y0, y1], [z0, z1], 'b-', linewidth=3, label="Link 1")
    ax.plot([x1, x2], [y1, y2], [z1, z2], 'g-', linewidth=3, label="Link 2")
    ax.plot([x2, x3], [y2, y3], [z2, z3], 'r-', linewidth=3, label="Link 3")
    ax.plot([x0, x1, x2, x3], [y0, y1, y2, y3], [z0, z1, z2, z3], 'ko-', markersize=8)  # Joints

    ax.scatter(target_pos[0], target_pos[1], target_pos[2], c='r', marker='x', s=100, label="Target Position")

    ax.set_xlim([-3, 3])
    ax.set_ylim([-3, 3])
    ax.set_zlim([-3, 3])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend()
    plt.draw()

def update(val):
    """Callback function to update the plot when sliders are adjusted."""
    target_pos = np.array([slider_x.val, slider_y.val, slider_z.val])
    joint_angles = inverse_kinematics(target_pos, initial_angles)
    plot_arm_3d(ax, *joint_angles, target_pos)

# Initial target position and angles
initial_angles = np.array([0.0, 0.0, 0.0])
initial_target_position = np.array([1.0, 1.0, 1.0])

# Create the figure and axis for 3D plot
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Initial plot
plot_arm_3d(ax, *initial_angles, initial_target_position)

# Create sliders for X, Y, and Z coordinates of the target position
ax_slider_x = plt.axes([0.25, 0.03, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_slider_y = plt.axes([0.25, 0.07, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_slider_z = plt.axes([0.25, 0.11, 0.65, 0.03], facecolor='lightgoldenrodyellow')

slider_x = Slider(ax_slider_x, 'X Target', -2.0, 2.0, valinit=initial_target_position[0])
slider_y = Slider(ax_slider_y, 'Y Target', -2.0, 2.0, valinit=initial_target_position[1])
slider_z = Slider(ax_slider_z, 'Z Target', -2.0, 2.0, valinit=initial_target_position[2])

# Call update function on slider change
slider_x.on_changed(update)
slider_y.on_changed(update)
slider_z.on_changed(update)

plt.show()
