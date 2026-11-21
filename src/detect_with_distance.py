import argparse
import cv2
import os
import time
import threading
import pyttsx3
import pigpio

from pycoral.adapters.common import input_size
from pycoral.adapters.detect import get_objects
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter, run_inference

# -----------------------------
# GLOBAL SHARED DISTANCE
# -----------------------------
current_distance = None
distance_lock = threading.Lock()

# -----------------------------
# TTS SETUP
# -----------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
speak_lock = threading.Lock()

def speak(text):
    def _speak():
        with speak_lock:
            engine.stop()
            engine.say(text)
            engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

# -----------------------------
# ULTRASONIC THREAD (pigpio)
# -----------------------------
def distance_thread():
    global current_distance

    TRIG = 23
    ECHO = 24

    pi = pigpio.pi()
    if not pi.connected:
        print("pigpio not connected")
        return

    pi.set_mode(TRIG, pigpio.OUTPUT)
    pi.set_mode(ECHO, pigpio.INPUT)
    pi.write(TRIG, 0)
    time.sleep(2.2)

    while True:
        # Trigger pulse
        pi.gpio_trigger(TRIG, 10, 1)

        start_time = time.time()
        timeout = start_time + 0.04

        while pi.read(ECHO) == 0:
            if time.time() > timeout:
                break
        pulse_start = time.time()

        while pi.read(ECHO) == 1:
            if time.time() > timeout:
                break
        pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = round(pulse_duration * 17150, 2)

        with distance_lock:
            current_distance = distance

        time.sleep(0.2)

# -----------------------------
# DRAW BOXES
# -----------------------------
def append_objs_to_img(cv2_im, inference_size, objs, labels):
    height, width, _ = cv2_im.shape
    scale_x, scale_y = width / inference_size[0], height / inference_size[1]

    for obj in objs:
        bbox = obj.bbox.scale(scale_x, scale_y)
        x0, y0 = int(bbox.xmin), int(bbox.ymin)
        x1, y1 = int(bbox.xmax), int(bbox.ymax)

        label = labels.get(obj.id, obj.id)
        score = int(obj.score * 100)

        text = f"{label} {score}%"
        cv2.rectangle(cv2_im, (x0, y0), (x1, y1), (0, 255, 0), 2)
        cv2.putText(cv2_im, text, (x0, y0 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    return cv2_im

# -----------------------------
# MAIN DETECTION
# -----------------------------
def main():
    global current_distance

    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='../all_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite')
    parser.add_argument('--labels', default='../all_models/coco_labels.txt')
    parser.add_argument('--threshold', type=float, default=0.4)
    parser.add_argument('--camera_idx', type=int, default=0)
    args = parser.parse_args()

    interpreter = make_interpreter(args.model)
    interpreter.allocate_tensors()
    labels = read_label_file(args.labels)
    inference_size = input_size(interpreter)

    cap = cv2.VideoCapture(args.camera_idx)

    last_spoken = ""
    last_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(rgb, inference_size)

        run_inference(interpreter, rgb.tobytes())
        objs = get_objects(interpreter, args.threshold)

        frame = append_objs_to_img(frame, inference_size, objs, labels)

        if objs:
            label = labels.get(objs[0].id, "object")

            with distance_lock:
                dist = current_distance

            if dist is not None:
                sentence = f"{label} {int(dist)} centimeters"
            else:
                sentence = f"{label} detected"

            now = time.time()
            if sentence != last_spoken and now - last_time > 1.5:
                speak(sentence)
                last_spoken = sentence
                last_time = now

        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# -----------------------------
# START EVERYTHING
# -----------------------------
if __name__ == "__main__":
    threading.Thread(target=distance_thread, daemon=True).start()
    main()
