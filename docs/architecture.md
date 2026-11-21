# Architecture

## Demonstrated configuration: `detect.py`

```
USB camera -> OpenCV frame capture -> BGR to RGB + resize
           -> MobileNet SSD v2 (PyCoral / Coral Edge TPU)
           -> detected class + bounding box
           -> offline pyttsx3 speech output
```

The demonstration version does not read ultrasonic distances.

## Standalone ranging: `latestDist.py`

```
HC-SR04 TRIG (GPIO 23) -> 10 microsecond trigger pulse
HC-SR04 ECHO (GPIO 24) -> high-pulse duration -> distance in cm
```

Approximate conversion: `distance_cm = pulse_duration_seconds * 17150`, using 343 m/s sound speed and dividing by two for the round trip. The standalone script busy-waits for pulse transitions and has no timeout protection.

## Integrated prototype: `detect_with_distance.py`

```
                           +-> background ultrasonic thread (pigpio) -+
                           |                                           v
Camera -> preprocessing -> Edge TPU detection -> read current_distance under lock
                                                -> TTS announcement thread
```

`threading.Lock()` protects `current_distance` updates/reads. Speech also uses a lock to serialize calls to the shared TTS engine, but a new background thread is started for each announcement. The camera and inference loop execute on the main thread.

The integrated script uses a default `0.4` confidence threshold; the demonstrated script uses `0.1` and limits displayed detections to three. That difference matters when comparing the outputs.

## System boundaries

A single ultrasonic sensor's returned distance cannot reliably be assigned to one specific visual bounding box. No tracked object-to-range association or path planning is implemented in the uploaded code.
