using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerController : MonoBehaviour
{

    public float sensitivity = 4;
    public float speed = 4;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // float rotateHorizontal = Input.GetAxis("Mouse X");
		// float rotateVertical = Input.GetAxis("Mouse Y");
		// transform.RotateAround (transform.position, -Vector3.up, rotateHorizontal * sensitivity * Time.deltaTime); //use transform.Rotate(-transform.up * rotateHorizontal * sensitivity) instead if you dont want the camera to rotate around the player
		// transform.RotateAround (Vector3.zero, transform.right, rotateVertical * sensitivity * Time.deltaTime); // again, use transform.Rotate(transform.right * rotateVertical * sensitivity) if you don't want the camera to rotate around the player

        float forward = Input.GetAxis("Vertical");
        transform.Translate(forward * speed * Vector3.forward) ;
        float rotate = Input.GetAxis("Horizontal");
        transform.Rotate(rotate * sensitivity * Vector3.up) ;
    }
}
