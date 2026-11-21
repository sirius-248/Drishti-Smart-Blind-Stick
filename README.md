# Drishti — Smart Blind Stick

**Vision Beyond Sight**

Drishti is an Edge-AI assistive-navigation prototype built around a Raspberry Pi 4B, a Coral USB Edge TPU, camera-based object detection, HC-SR04 ultrasonic ranging, and offline text-to-speech feedback.

## Implementation status

- **`src/detect.py` — demonstrated program.** Used during the project presentation. Runs camera-based object detection and announces detected labels using offline text-to-speech. The team reports this script was configured to launch at Raspberry Pi startup; that startup configuration is not included here.
- **`src/latestDist.py` — standalone ultrasonic ranging.** Measures and prints distance in centimeters using GPIO 23 (TRIG) and GPIO 24 (ECHO).
- **`src/detect_with_distance.py` — integrated prototype.** Combines object detection with background ultrasonic measurements and spoken distance notifications. Its actual runtime FPS has not been independently verified.

All three scripts are preserved as originally supplied. **The presentation ran `detect.py`, not the integrated script**. Do not assume the presentation demonstrated simultaneous object classification and distance announcements.

## System components

| Part | Role |
| --- | --- |
| Raspberry Pi 4B | Host processing and hardware I/O |
| USB camera | Captures frames |
| Google Coral USB Accelerator | Runs Edge TPU-compatible object-detection model |
| HC-SR04 ultrasonic sensor | Measures echo pulse duration to estimate distance |
| Audio output + `pyttsx3` | Announces object labels, and optionally distances in the integrated prototype |

## Model

The detection scripts default to:

- `../all_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite`
- `../all_models/coco_labels.txt`

These are paths expected by the code, **not model files included in this repository**. This implementation uses **MobileNet SSD v2 on Coral Edge TPU**, not YOLOv8. The model and labels must be obtained separately and paths adjusted as needed. Relative paths depend on the process working directory.

## What the code does

1. OpenCV reads video frames from the selected camera.
2. Frames are converted from BGR to RGB and resized to the model input size.
3. PyCoral invokes Edge TPU inference and returns detected objects, confidence scores, and bounding boxes.
4. `detect.py` announces the first returned class label, with a simple repetition/time guard.
5. In the integrated prototype, a separate thread regularly measures distance, updates a lock-protected shared variable, and the detection loop reads it for speech output.

The ultrasonic reading is not guaranteed to correspond to the particular camera-detected object; it measures an echo from an object in the sensor's field of view.

## Running on Raspberry Pi

Prerequisites include a Raspberry Pi with appropriate GPIO connections, a working Coral USB Accelerator and PyCoral runtime, OpenCV, `pyttsx3`, and either `RPi.GPIO` (standalone ranging) or `pigpio` (integrated ranging). Compatible package/runtime versions depend on the installed Raspberry Pi OS and Python version; these were not preserved in the supplied files.

From the `src/` directory (with model files located in an adjacent `all_models/` directory):

```bash
python3 detect.py
python3 latestDist.py
python3 detect_with_distance.py
```

The camera and accelerator must be connected; the distance scripts require the ultrasonic sensor to be wired correctly. For `pigpio`, the daemon must be running. **Check electrical level compatibility of the HC-SR04 echo signal with Raspberry Pi GPIO before connecting hardware.**

For another model location, `detect.py` accepts `--model` and `--labels` arguments. `detect_with_distance.py` supports the same arguments.

## Limitations and evidence

- The three uploaded scripts do not contain benchmarking/evaluation instrumentation. **No FPS, precision, recall, F1, accuracy, or distance-error numbers are claimed as measured results here.**
- The IEEE conference paper associated with this project includes performance figures, but the team has clarified these were not measured and **must not be treated as verified**.
- The integrated prototype's speed has not been established through repeatable profiling.
- The code does not implement collision-free route planning or safety-certified navigation.

See [`docs/architecture.md`](docs/architecture.md) and [`docs/implementation-notes.md`](docs/implementation-notes.md) for design details and interview-study topics.

## Research context

Related paper: *Real-Time Assistive Navigation for Visually Impaired Users Using Edge-AI Object Detection and Ultrasonic Distance Sensing*, 2026 IEEE DISCOVER. [DOI: 10.1109/DISCOVER70666.2026.11766501](https://doi.org/10.1109/DISCOVER70666.2026.11766501).

This repository does not reproduce the publisher's PDF or endorse its unverified experimental figures. Best Paper recognition is reported by the team; award documentation is not included.

## Project collaborators

Developed as a team project. Original paper credits Shashank Ravindra, B Abhitha Bhat, Gaurav S B, Ananya Raghuveer, and Nandita Bangera. Confirm author/contributor permissions and licensing before making this repository public.

## License

No license has been selected. Do not assume reuse rights; confirm agreement with collaborators and any intellectual-property obligations first.
