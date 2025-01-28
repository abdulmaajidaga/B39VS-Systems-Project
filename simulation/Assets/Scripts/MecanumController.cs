using System.Collections;
using System.Collections.Generic;
using RosMessageTypes.Hazmat;
using Unity.Robotics.ROSTCPConnector;
using UnityEngine;

public class MecanumController : MonoBehaviour
{

    [SerializeField]
    Transform[] wheels;
    [SerializeField]
    float speed = 4;

    // Rigidbody body;

    ROSConnection ros;

    void Start()
    {
        // body = GetComponent<Rigidbody>();
        
        ros = ROSConnection.GetOrCreateInstance();
        ros.Subscribe<MecanumCmdMsg>("/wheel_cmd", callback);
    }

    // Update is called once per frame
    void callback(MecanumCmdMsg msg)
    {
        Debug.Log(wheels[0].localPosition);
        wheels[0].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, speed * msg.front_right);
        wheels[1].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, speed * msg.front_left);
        wheels[2].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, speed * msg.rear_right);
        wheels[3].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, speed * msg.rear_left);
        // (speed * msg.front_right * Vector3.forward, wheels[0].localPosition, ForceMode.Acceleration);
    }
}
