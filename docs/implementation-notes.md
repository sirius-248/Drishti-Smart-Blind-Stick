
# Drishti — Implementation Details

## Overview

This document describes the software implementation of Drishti, an Edge-AI-based assistive navigation system developed using Python, Raspberry Pi, Google Coral Edge TPU, OpenCV, and ultrasonic sensing.

The implementation focuses on object recognition, proximity measurement, concurrent sensor processing, and offline voice feedback.

The project contains three Python scripts representing its primary software components.

## 1. Project Source Files

| File | Functionality |
|---|---|
| `detect.py` | Object detection with voice feedback |
| `latestDist.py` | Ultrasonic distance measurement |
| `detect_with_distance.py` | Integrated object detection and distance sensing |

### Implementation Overview

The primary object detection program, `detect.py`, was used during the final project presentation.

The integrated implementation, `detect_with_distance.py`, combines camera-based object recognition and ultrasonic sensing into a single program.

The `latestDist.py` script provides standalone ultrasonic distance measurement.

## 2. Object Detection — detect.py

### Purpose

The `detect.py` program performs camera-based object recognition using a MobileNet-SSD V2 model accelerated by the Google Coral Edge TPU.

It also provides audio announcements for detected objects.

### Libraries

- `cv2` — Camera capture, image processing, and visualization
- `pycoral` — Coral Edge TPU model execution
- `pyttsx3` — Offline text-to-speech
- `threading` — Background audio execution
- `time` — Announcement timing
- `argparse` — Runtime configuration

### Step 1: Model Initialization

The program loads an Edge TPU-compatible TensorFlow Lite model through PyCoral.

```python
interpreter = make_interpreter(args.model)
interpreter.allocate_tensors()

labels = read_label_file(args.labels)
inference_size = input_size(interpreter)
```

The interpreter initializes the neural network and allocates the tensors required for inference.

The label file maps prediction IDs to readable object names.

### Step 2: Camera Initialization

```python
cap = cv2.VideoCapture(args.camera_idx)
```

OpenCV initializes the camera stream.

The program continuously reads frames for processing.

### Step 3: Image Preprocessing

```python
cv2_im_rgb = cv2.cvtColor(
    cv2_im, cv2.COLOR_BGR2RGB
)

cv2_im_rgb = cv2.resize(
    cv2_im_rgb, inference_size
)
```

Each camera frame is converted into RGB format and resized to the dimensions expected by the model.

This prepares the image for neural network inference.

### Step 4: Object Detection

```python
run_inference(
    interpreter,
    cv2_im_rgb.tobytes()
)

objs = get_objects(
    interpreter, args.threshold
)[:args.top_k]
```

The processed image is passed to the Coral Edge TPU.

The model returns detected objects and associated predictions.

The script uses a configurable confidence threshold and limits the number of selected detections.

### Step 5: Bounding Box Visualization

The detection coordinates are scaled from model-input dimensions to the original camera frame dimensions.

```python
scale_x = width / inference_size[0]
scale_y = height / inference_size[1]

bbox = obj.bbox.scale(scale_x, scale_y)
```

OpenCV is then used to draw bounding rectangles and display object labels with confidence percentages.

### Step 6: Voice Feedback

Drishti uses `pyttsx3` to announce detected objects.

```python
engine = pyttsx3.init()
engine.setProperty('rate', 150)
```

The program maintains the last announced object label and the timestamp of the previous announcement.

A new announcement is generated when the detected label changes and the configured time interval has elapsed.

Speech execution is handled through a background thread.



## 3. Distance Measurement — latestDist.py

### Purpose

The `latestDist.py` program performs distance sensing using the HC-SR04 ultrasonic sensor connected to the Raspberry Pi GPIO interface.

### Libraries

- `RPi.GPIO` — GPIO pin control
- `time` — Trigger timing and pulse measurement

### GPIO Configuration

```python
GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
```

The program configures GPIO 23 for transmitting the trigger pulse and GPIO 24 for receiving the echo response.

### Trigger Signal

```python
GPIO.output(TRIG, True)
time.sleep(0.00001)
GPIO.output(TRIG, False)
```

A trigger pulse lasting approximately 10 microseconds initiates the ultrasonic measurement.

### Echo Measurement

The program observes changes in the echo pin to determine the duration of the returned signal.

```python
pulse_duration = pulse_end - pulse_start
```

### Distance Calculation

```python
distance = pulse_duration * 17150
distance = round(distance, 2)
```

The distance is calculated in centimeters using the speed of sound and the measured pulse duration.

### Output

The calculated distance is printed to the terminal.

Example:

```text
Distance: 125.45 cm
```

The measurement cycle repeats continuously, with a short delay between readings.


## 4. Integrated Detection — detect_with_distance.py

### Purpose

The integrated implementation combines camera-based object detection and ultrasonic proximity sensing to produce spoken feedback containing both object identity and distance.

It brings together the computer vision and embedded sensing components within a single Python application.

### Libraries

- `cv2` — Camera processing and visualization
- `pycoral` — Edge TPU inference
- `pigpio` — Ultrasonic sensor GPIO operations
- `pyttsx3` — Voice feedback
- `threading` — Concurrent execution
- `time` — Sensor and audio timing

### Step 1: Shared Distance State

```python
current_distance = None
distance_lock = threading.Lock()
```

The latest ultrasonic reading is stored in a shared variable.

A lock coordinates access to the variable between the distance measurement thread and the main detection loop.

### Step 2: Ultrasonic Measurement Thread

The integrated implementation uses the `pigpio` library to control the ultrasonic sensor.

```python
pi = pigpio.pi()

pi.set_mode(TRIG, pigpio.OUTPUT)
pi.set_mode(ECHO, pigpio.INPUT)
```

The sensor is triggered periodically, and its echo duration is used to calculate distance.

The latest measurement is stored in the shared variable.

```python
with distance_lock:
    current_distance = distance
```

### Step 3: Object Detection

The main thread captures camera frames and performs object detection through the Coral Edge TPU.

```python
run_inference(
    interpreter, rgb.tobytes()
)

objs = get_objects(
    interpreter, args.threshold
)
```

The output includes detected object classes, bounding boxes, and confidence scores.

### Step 4: Combining Object and Distance Information

The program retrieves the label of the first detected object and reads the latest distance value.

```python
label = labels.get(objs[0].id, "object")

with distance_lock:
    dist = current_distance
```

The information is combined into a spoken sentence.

```python
if dist is not None:
    sentence = f"{label} {int(dist)} centimeters"
else:
    sentence = f"{label} detected"
```

### Step 5: Audio Announcements

The integrated program generates voice announcements through `pyttsx3`.

Speech requests are executed in background threads, while a lock coordinates access to the shared text-to-speech engine.

The program also uses announcement timing and label comparison to manage repeated messages.



## 5. Threading and Synchronization

Python threading is used to coordinate the software components of the integrated implementation.

### Main Execution Thread

Responsible for:

- Camera frame acquisition
- Image preprocessing
- Edge TPU inference
- Detection visualization
- Combining detection and distance information

### Ultrasonic Measurement Thread

Responsible for:

- Sending ultrasonic trigger pulses
- Receiving echo signals
- Calculating distance
- Updating the shared distance measurement

### Speech Execution

Responsible for:

- Converting detection information into audio
- Running spoken announcements
- Coordinating access to the TTS engine

### Thread Locks

The implementation uses two synchronization locks.

**Distance Lock**

Coordinates access to the latest ultrasonic reading.

**Speech Lock**

Coordinates access to the shared `pyttsx3` engine.

This separation supports concurrent sensor acquisition, object recognition, and audio feedback.

## 6. TensorFlow Lite and Coral Edge TPU

### Model

The project uses the Edge TPU-compatible MobileNet-SSD V2 TensorFlow Lite model:

```text
mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
```

The associated labels are loaded from:

```text
coco_labels.txt
```

### Why MobileNet-SSD V2?

MobileNet-SSD combines an efficient feature extraction backbone with a Single Shot Detector.

Its architecture is well-suited to embedded computer vision applications where processing resources and inference latency are important design considerations.

### Why Coral Edge TPU?

The Google Coral USB Accelerator provides dedicated hardware for supported quantized neural network operations.

By executing object detection locally, the system reduces dependence on cloud services and supports offline operation.

### PyCoral Integration

PyCoral provides the software interface between the TensorFlow Lite detection model and the Coral Edge TPU.

It supports model initialization, inference execution, and extraction of object detection results.

## 7. Audio Feedback System

Drishti uses the offline `pyttsx3` text-to-speech library.

The audio system translates detection information into spoken feedback.

### Object Detection Mode

Example announcement:

```text
Person
```

### Integrated Detection Mode

Example announcement:

```text
Chair 90 centimeters
```

Audio feedback is a core part of Drishti's accessibility-oriented design, allowing obstacle information to be communicated without requiring the user to view a screen.

## 8. Raspberry Pi Deployment

The project is designed to run on a Raspberry Pi 4B with an attached USB camera, Google Coral USB Accelerator, ultrasonic sensor, and audio output.

The demonstration setup used `detect.py` as the object detection program launched on startup.

The software performs local inference and provides spoken object recognition feedback.

### Model Assets

The Python detection scripts reference an `all_models` directory containing the TensorFlow Lite model and its corresponding labels.

The model and labels can also be supplied through command-line arguments.

### Core Software Stack

| Technology | Role |
|---|---|
| Python | Main programming language |
| OpenCV | Image acquisition and processing |
| TensorFlow Lite | Model format and inference runtime |
| PyCoral | Edge TPU integration |
| MobileNet-SSD V2 | Object detection architecture |
| RPi.GPIO | Standalone ultrasonic sensor control |
| pigpio | Integrated ultrasonic sensor control |
| pyttsx3 | Offline voice feedback |
| Python threading | Concurrent execution |

## 9. Research and Recognition

Drishti was developed as an assistive technology project integrating embedded computing, computer vision, and real-time sensing.

The project was presented at the 2026 IEEE International Conference on Distributed Computing, VLSI, Electrical Circuits and Robotics (DISCOVER).

**Publication:**

Real-Time Assistive Navigation for Visually Impaired Users Using Edge-AI Object Detection and Ultrasonic Distance Sensing

**IEEE DOI:**

https://doi.org/10.1109/DISCOVER70666.2026.11766501

**Award:**

Best Paper Award

The project demonstrates the application of Edge AI and embedded systems to accessibility-focused technology.
