# Implementation notes and interview preparation

## What was demonstrably implemented

- `detect.py`: PyCoral inference of a Coral-compatible MobileNet SSD v2 `.tflite` model, OpenCV camera capture, bounding-box overlays, `pyttsx3` speech announcements.
- `latestDist.py`: HC-SR04 distance calculation with `RPi.GPIO`.
- `detect_with_distance.py`: concurrent range acquisition with `pigpio`, lock-protected current distance, combined spoken object-label + distance alerts.

## What remains to verify

- Pi power-on autostart unit/cron entry and run command.
- Actual deployed `.tflite` and labels files, OS/Python/dependency versions.
- Runtime FPS of each implementation and audio latency, measured with profiling rather than memory.
- Any separate scripts/datasets used for real evaluations.
- Safe electrical connections and stable power supply details.

## Engineering discussion points

1. Why choose a lightweight MobileNet SSD detector and an Edge TPU instead of CPU-only inference?
2. What is quantization, and why does an Edge TPU require a compatible compiled model?
3. What does SSD predict, and how do bounding-box coordinates get resized to the displayed frame?
4. Why convert camera BGR to RGB? What happens with an incorrect model input size?
5. What do confidence thresholds `0.1` and `0.4` change?
6. Derive the ultrasonic distance formula from the round-trip echo time.
7. How do shared state and locks work in the integrated script? What if the distance becomes stale?
8. Could creating a new thread per audio announcement create contention or queues?
9. Why might the integrated code feel slower? Which timings would distinguish capture, preprocessing, inference, GUI, GPIO polling, and TTS overhead?
10. Why doesn't a distance reading necessarily belong to the visually detected object?

## Research-report caution

The related IEEE paper reports numerical benchmarking and evaluation outcomes, but the team has stated those results were not actually measured. They are **not evidence of performance**. A valid evaluation requires recording genuine predictions and ground-truth labels and measuring real timing/sensor data. Do not recreate or cite the published numerical claims as verified project outcomes.
