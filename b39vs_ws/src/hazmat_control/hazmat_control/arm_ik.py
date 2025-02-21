import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import PyKDL as kdl
from . import urdf as kdl_parser


class Arm_IK(Node):
    def __init__(self):
        super().__init__('arm_ik')

        # Subscription to /robot_description topic
        self.subscription = self.create_subscription(
            String,
            'robot_description',
            self.robot_description_callback,
            10
        )
        self.subscription  # prevent unused variable warning

        self.tree = kdl.Tree()
        self.chain = kdl.Chain()
        self.solver = None

    def robot_description_callback(self, msg):
        # Construct KDL tree from URDF string
        urdf = msg.data
        success, self.tree = kdl_parser.treeFromString(urdf)

        if success:
            self.get_logger().info('KDL Tree constructed successfully.')
            self.get_logger().info(f'Number of joints: {self.tree.getNrOfJoints()}')
            self.get_logger().info(f'Number of segments: {self.tree.getNrOfSegments()}')
            self.get_logger().info(f'Root segment: {self.tree.getRootSegment().getName()}')

            # Create a kinematic chain from base_link to foot
            if self.tree.getChain('base_link', 'foot', self.chain):
                self.solver = kdl.ChainIkSolverPos_LMA(self.chain)  # Inverse Kinematics Solver (Levenberg-Marquardt)
            else:
                self.get_logger().error('Failed to extract kinematic chain from URDF.')
        else:
            self.get_logger().error('Failed to construct KDL Tree from URDF.')

    def get_joint_angles(self, x, z):
        if self.solver is None:
            self.get_logger().error('IK solver has not been initialized.')
            return None

        # Prepare IK solver input variables
        q_init = kdl.JntArray(self.chain.getNrOfJoints())
        q_init[0] = -0.1
        q_init[1] = 0.2

        p_in = kdl.Frame(kdl.Vector(x, 0.0, z))  # Cartesian coordinates (x, z)
        q_out = kdl.JntArray(self.chain.getNrOfJoints())

        # Run IK solver
        result = self.solver.CartToJnt(q_init, p_in, q_out)
        if result >= 0:
            self.get_logger().info(f'Hip joint angle: {q_out[0]:.2f} rad')
            self.get_logger().info(f'Knee joint angle: {q_out[1]:.2f} rad')
            return q_out[0], q_out[1]  # Return hip and knee joint angles
        else:
            self.get_logger().error('Could not solve inverse kinematics.')
            return None

def main(args=None):
    rclpy.init(args=args)

    node = Arm_IK()

    # Wait for the /robot_description topic to receive the URDF
    while rclpy.ok():
        rclpy.spin_once(node)
        # Example target pose in Cartesian coordinates
        target_x = 0.3
        target_z = -0.6
        angles = node.get_joint_angles(target_x, target_z)
        if angles is not None:
            hip_angle, knee_angle = angles
            node.get_logger().info(f'Angles for x={target_x}, z={target_z}: Hip={hip_angle}, Knee={knee_angle}')
            break

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
