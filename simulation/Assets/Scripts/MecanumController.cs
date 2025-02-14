using System.Collections;
using System.Collections.Generic;
using RosMessageTypes.Hazmat;
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

    ArticulationBody body;

    ROSConnection ros;

    Vector3 targetVelocity = new();
    float targetOmega = 0;

    void Start()
    {
        body = GetComponent<ArticulationBody>();
        
        ros = ROSConnection.GetOrCreateInstance();
        ros.Subscribe<MecanumCmdMsg>("/wheel_cmd", callback);
    }

    void FixedUpdate()
    {
        body.velocity = targetVelocity;
        body.angularVelocity = targetOmega * Vector3.up;
    }

    // Update is called once per frame
    void callback(MecanumCmdMsg msg)
    {
        // wheels[0].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[0] * speed * msg.front_right);
        // wheels[1].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[1] * speed * msg.front_left);
        // wheels[2].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[2] * speed * msg.rear_right);
        // wheels[3].GetChild(0).GetComponent<ArticulationBody>().SetDriveTargetVelocity(ArticulationDriveAxis.X, wheelCalibrations[3] * speed * msg.rear_left);

        // (speed * msg.front_right * Vector3.forward, wheels[0].localPosition, ForceMode.Acceleration);

        
        // Unity coordinate systems uses Z as forward and X as right
        targetVelocity.z = speed * radiusValue * (msg.front_left + msg.front_right + msg.rear_left + msg.rear_right);
        targetVelocity.x = speed * radiusValue * (-msg.front_left + msg.front_right + msg.rear_left - msg.rear_right);
        targetOmega = radiusValue * (-msg.front_left + msg.front_right - msg.rear_left + msg.rear_right) * distanceSum;
        Debug.Log(targetVelocity);
    }
}
