
# Drishti — System Architecture

## Overview

Drishti is an Edge-AI-powered assistive navigation system designed to help visually impaired individuals recognize obstacles in their surroundings through object detection, ultrasonic distance sensing, and voice feedback.

The system combines computer vision and embedded hardware to provide an accessible, portable, and offline navigation assistance solution.

At the center of Drishti is a Raspberry Pi 4B, which coordinates input from a USB camera and an HC-SR04 ultrasonic sensor. A Google Coral USB Accelerator handles neural network inference, enabling object recognition directly on the device.

The architecture brings together three major functions:

1. Real-time object recognition
2. Ultrasonic proximity sensing
3. Audio-based feedback

## 1. Hardware Architecture

### Prototype

<img width="517" height="219" alt="image" src="https://github.com/user-attachments/assets/83cb9bd7-3a54-486d-ac54-1555980f2643" />



### Hardware Components

<img width="507" height="211" alt="image" src="https://github.com/user-attachments/assets/2d9f056e-3a76-42d8-9556-6acaad24b741" />

| Component | Purpose |
|---|---|
| Raspberry Pi 4B | Central processing and system coordination |
| Google Coral USB Accelerator | Hardware-accelerated AI inference |
| USB Camera | Captures the surrounding environment |
| HC-SR04 Ultrasonic Sensor | Measures the distance to nearby obstacles |
| Audio Output Device | Delivers spoken navigation feedback |
| Power Bank | Provides portable power to the system |

### Hardware Integration

The Raspberry Pi acts as the central controller, connecting the computer vision, distance sensing, and audio modules.

The camera supplies visual information for object recognition, while the ultrasonic sensor independently measures the proximity of obstacles.

The Coral Edge TPU accelerates object detection, allowing the system to process neural network operations locally without relying on cloud services.

## 2. System Architecture

The architecture consists of two sensing pipelines coordinated by the Raspberry Pi.

### Visual Detection Pipeline

The camera captures frames of the surrounding environment. These frames are preprocessed and passed to a MobileNet-SSD V2 model running through the Coral Edge TPU.
The detection model identifies objects and produces class labels, confidence scores, and bounding boxes. The system converts detection information into spoken announcements using the offline `pyttsx3` text-to-speech engine. In the integrated implementation, the detected object label is combined with the latest ultrasonic distance reading.

### Distance Measurement Pipeline

The HC-SR04 ultrasonic sensor measures obstacle proximity using the time-of-flight principle.

The Raspberry Pi receives the sensor's echo signal through its GPIO interface and calculates the corresponding distance.

For example:

"Chair 90 centimeters"

## 3. Object Detection Architecture

Drishti uses a quantized MobileNet-SSD V2 model with Google's Coral Edge TPU for object detection.

### Processing Stages

1. Capture a frame using the USB camera.
2. Convert the image from BGR to RGB using OpenCV.
3. Resize the image to the model's expected input dimensions.
4. Perform inference through PyCoral and the Coral Edge TPU.
5. Retrieve object labels, confidence scores, and bounding boxes.
6. Display detected objects on the camera frame.
7. Generate spoken feedback for the detected object.

### Detection Model

**Model:** MobileNet-SSD V2

**Framework:** TensorFlow Lite

**Hardware Acceleration:** Google Coral Edge TPU

**Dataset Family:** MS-COCO

MobileNet provides an efficient convolutional neural network architecture suitable for resource-constrained systems.

The Single Shot Detector (SSD) architecture performs object localization and classification in a single detection pass.

The quantized TensorFlow Lite model is deployed using PyCoral to take advantage of Edge TPU acceleration.

### Detection Examples

<img width="610" height="278" alt="image" src="https://github.com/user-attachments/assets/040eae07-7840-43cc-9e12-93d59c5abc1c" />


## 4. Ultrasonic Distance Sensing

Drishti integrates an HC-SR04 ultrasonic sensor to estimate the distance between the device and nearby obstacles.

### Sensor Configuration

| Pin | Raspberry Pi Connection |
|---|---|
| TRIG | GPIO 23 (BCM) |
| ECHO | GPIO 24 (BCM) |

### Distance Measurement Principle

The sensor emits an ultrasonic pulse and measures the time taken for the reflected signal to return.

Since the sound wave travels to the obstacle and back, the total travel distance is twice the distance between the sensor and the obstacle.

The distance is calculated using:

Distance = (Time × Speed of Sound) / 2

Taking the speed of sound as approximately 343 m/s:

Distance (cm) = Pulse Duration (seconds) × 17150

The calculated distance can be incorporated into audio announcements alongside object recognition results.

### Sensor Circuit

<img width="457" height="220" alt="image" src="https://github.com/user-attachments/assets/84ee83d0-144e-4e70-a036-c54cb5023e5a" />


## 5. Integrated System Workflow

The integrated implementation combines visual object recognition and ultrasonic sensing through concurrent execution.

### Workflow

1. Initialize the camera, detection model, and text-to-speech engine.
2. Start ultrasonic distance measurements in a background thread.
3. Continuously capture camera frames.
4. Perform object detection using the Coral Edge TPU.
5. Retrieve the latest ultrasonic distance reading.
6. Combine the detected object label and distance.
7. Generate spoken feedback.
8. Continue monitoring the environment.

### Operational Flowchart

<img width="394" height="487" alt="image" src="https://github.com/user-attachments/assets/e424e7ac-581e-4bdf-a9be-0762655668ac" />


## 6. Concurrent Processing

The integrated system uses Python threading to coordinate detection, sensing, and speech.

**Main Thread**

Handles camera capture, image preprocessing, object detection, and visualization.

**Ultrasonic Sensor Thread**

Continuously measures obstacle proximity and updates the shared distance variable.

**Speech Threads**

Handle spoken announcements using the text-to-speech engine.

Thread synchronization locks coordinate access to shared distance information and the speech engine.

This design allows the sensing and feedback components to operate concurrently.

## 7. Offline Edge-AI Processing

A central feature of Drishti is its ability to perform object detection without requiring an active internet connection.

Object detection is executed locally using the Coral Edge TPU, while proximity measurements are obtained directly from the ultrasonic sensor.

The text-to-speech module also operates locally.

This approach reduces dependence on cloud-based processing and supports portable assistive applications.

## 8. Research Publication

The Drishti project was presented at the 2026 IEEE International Conference on Distributed Computing, VLSI, Electrical Circuits and Robotics (DISCOVER).

**Paper:** Real-Time Assistive Navigation for Visually Impaired Users Using Edge-AI Object Detection and Ultrasonic Distance Sensing

**DOI:** https://doi.org/10.1109/DISCOVER70666.2026.11766501

**Recognition:** Best Paper Award

The research presents the design and methodology of the Edge-AI assistive navigation system.
