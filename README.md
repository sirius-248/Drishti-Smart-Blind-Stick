<div align="center">

# Drishti — Smart Blind Stick

### Vision Beyond Sight

**An Edge-AI-powered assistive navigation prototype designed to make surrounding obstacles easier to recognize through real-time object detection, ultrasonic sensing, and spoken feedback.**

**IEEE DISCOVER 2026 · Best Paper Award (team-reported)**

</div>

---

## Overview

Drishti explores how compact, affordable hardware can support more informed mobility for people with visual impairments. Built on a **Raspberry Pi 4B**, the project brings together **camera-based object recognition**, **Google Coral Edge TPU acceleration**, **ultrasonic distance sensing**, and **offline voice guidance**.

Rather than requiring an internet connection for object recognition, the prototype performs inference locally on its edge hardware. The project brings computer vision and embedded sensing together in an assistive technology application.

## Highlights

- **Real-time object recognition:** identifies everyday objects using a MobileNet SSD v2 detector.
- **On-device AI inference:** uses a quantized TensorFlow Lite model compatible with the Google Coral USB Accelerator.
- **Spoken feedback:** converts detected object labels into audio notifications with offline text-to-speech.
- **Ultrasonic proximity sensing:** measures nearby obstacle distance using the HC-SR04 sensor.
- **Integrated exploration:** combines object labels and distance readings into spoken messages in a dedicated prototype.
- **Portable embedded design:** developed around Raspberry Pi hardware and widely available components.

## Technology stack

| Area | Technology |
| --- | --- |
| Embedded computing | Raspberry Pi 4B |
| AI acceleration | Google Coral USB Edge TPU |
| Object detection | MobileNet SSD v2, TensorFlow Lite, PyCoral |
| Computer vision | OpenCV, USB camera |
| Proximity sensing | HC-SR04 ultrasonic sensor, Raspberry Pi GPIO |
| Voice output | Python `pyttsx3` |
| Implementation | Python, multithreading |

## How Drishti works

```text
                     DRISHTI
                        |
          +-------------+-------------+
          |                           |
       USB camera                HC-SR04 sensor
          |                           |
    OpenCV capture             Echo pulse timing
          |                           |
   RGB + resize               Distance estimate
          |                           |
   MobileNet SSD v2                  |
    on Coral Edge TPU                |
          |                           |
    Object label + score             |
          +-------------+-------------+
                        |
               Audio feedback
                (offline TTS)
```

The object detection path captures frames, preprocesses them for the model, executes accelerated inference, and announces recognized objects. The integrated script also reads the latest ultrasonic distance to generate messages containing both an object label and an approximate distance.

## Project source code

| File | Purpose |
| --- | --- |
| [`src/detect.py`](src/detect.py) | Main object-detection and voice-feedback program; used for the final presentation |
| [`src/detect_with_distance.py`](src/detect_with_distance.py) | Integrated object recognition, ultrasonic ranging, and audio feedback |
| [`src/latestDist.py`](src/latestDist.py) | Standalone ultrasonic distance sensing |

All three scripts are included to show the system's major functional modules. The **final presentation used `detect.py`**, while the combined implementation is available for exploring sensor integration.

## Model and setup

The detection scripts reference the **Edge TPU-compiled MobileNet SSD v2 COCO model**:

```text
mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite
coco_labels.txt
```

Place the compatible model and label files in the `all_models/` directory adjacent to `src/`, or pass their paths using the `--model` and `--labels` options.

The original Python scripts are provided as-is. Running them requires a configured Raspberry Pi environment with the Coral runtime, PyCoral, OpenCV, `pyttsx3`, and appropriate GPIO libraries. For ultrasonic sensing, connect the HC-SR04 using Pi-safe signal levels and the project's GPIO mapping (TRIG: BCM 23, ECHO: BCM 24).

From `src/`, run the desired module:

```bash
python3 detect.py
# or
python3 latestDist.py
# or
python3 detect_with_distance.py
```

These are **alternative entry points**, not commands that must all run simultaneously. The integrated program requires `pigpio` to be available and its daemon running.

## Engineering behind Drishti

Drishti combines several important embedded AI ideas:

**Edge inference.** MobileNet SSD v2 provides an efficient single-shot object detector, while Coral hardware runs compatible quantized operations locally.

**Sensor-based ranging.** The HC-SR04 estimates distance from the time taken for an ultrasonic pulse to travel to an obstacle and return:

`distance_cm = echo_duration_seconds × 17150`

**Concurrent sensing.** The integrated script collects ultrasonic data in a background thread and accesses the shared measurement using a lock, allowing the detection loop to use the latest reading during voice announcements.

**Accessible feedback.** Offline speech output translates detections into short audio prompts, focusing the interface on spoken information rather than requiring a screen.

Further explanations are in [`docs/architecture.md`](docs/architecture.md) and [`docs/implementation-notes.md`](docs/implementation-notes.md).

## Research and recognition

The project was presented in connection with the **2026 IEEE International Conference on Distributed Computing, VLSI, Electrical Circuits and Robotics (DISCOVER)** and received a **Best Paper Award**, as reported by the team.

**Paper:** *Real-Time Assistive Navigation for Visually Impaired Users Using Edge-AI Object Detection and Ultrasonic Distance Sensing*

**Publication:** [IEEE DOI: 10.1109/DISCOVER70666.2026.11766501](https://doi.org/10.1109/DISCOVER70666.2026.11766501)

The publication documents the motivation, architecture, hardware and experimental framework for the project. This repository focuses on the **actual implementation and its underlying design**, rather than publishing benchmark claims without reproducible test data.

## Team

** Gaurav S B · B Abhitha Bhat ·  Ananya Raghuveer · Shashank Ravindra · Nandita Bangera**

*Developed as an academic research and engineering project at RV Institute of Technology and Management, Bengaluru.*

---

<div align="center">

**Drishti — Vision Beyond Sight**

*Exploring accessible mobility through embedded intelligence.*

</div>
