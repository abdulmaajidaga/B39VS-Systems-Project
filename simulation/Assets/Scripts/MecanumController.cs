using System.Collections;
using System.Collections.Generic;
using RosMessageTypes.Geometry;
using Unity.Robotics.ROSTCPConnector;
using UnityEngine;

public class MecanumController : MonoBehaviour
{

    [SerializeField]
    Transform[] wheels;
    [Range(0, 1), SerializeField]
    float[] wheelCalibrations;
    [SerializeField]
    float speed = 0.004f;

    float radiusValue = 38.5f / 4f;
    float distanceSum = 1 / (0.5f + 0.5f);

    // ArticulationBody body;
    Rigidbody body;

    ROSConnection ros;

    // Vector3 targetVelocity = new();
    float targetOmega = 0;
    float linearX = 0;
    float linearY = 0;

    void Start()
    {
        // body = GetComponent<ArticulationBody>();
        body = GetComponent<Rigidbody>();
        
        ros = ROSConnection.GetOrCreateInstance();
        // ros.Subscribe<MecanumCmdMsg>("/hazmat/wheel_cmd", callback);
        ros.Subscribe<TwistMsg>("/hazmat/cmd_vel", callback);
    }

    void FixedUpdate()
    {
        Debug.Log(linearX);
        body.velocity = speed * new Vector3(-linearY, 0, linearX);
        body.angularVelocity = speed * targetOmega * Vector3.up;
    }

    // Update is called once per frame
    void callback(TwistMsg msg)
    {
        Debug.Log("command recieved");
        targetOmega = (float) msg.angular.z;
        linearX = (float) msg.linear.x;
        linearY = (float) msg.linear.y;
        // wheels[0].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[0] * speed * msg.front_right);
        // wheels[1].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[1] * speed * msg.front_left);
        // wheels[2].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[2] * speed * msg.rear_right);
        // wheels[3].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[3] * speed * msg.rear_left);

        // (speed * msg.front_right * Vector3.forward, wheels[0].localPosition, ForceMode.Acceleration);

        
        // Unity coordinate systems uses Z as forward and X as right
        // targetVelocity.z = speed * radiusValue * (msg.front_left + msg.front_right + msg.rear_left + msg.rear_right);
        // targetVelocity.x = speed * radiusValue * (-msg.front_left + msg.front_right + msg.rear_left - msg.rear_right);
        // targetOmega = radiusValue * (-msg.front_left + msg.front_right - msg.rear_left + msg.rear_right) * distanceSum;
        // Debug.Log(targetVelocity);
    }
}
