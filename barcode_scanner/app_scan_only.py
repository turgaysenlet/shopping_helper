import os
from fastapi import FastAPI, BackgroundTasks
from pyzbar.pyzbar import decode
import cv2
import threading
import time

app = FastAPI()

camera_thread = None
is_running = False


def start_camera():
    global is_running
    is_running = True

    # Set the environment variable
    os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '1'

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("OpenCV: camera failed to properly initialize!")
        return

    frame_skip = 5  # Only process every 5th frame
    frame_count = 0

    while is_running:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        # Resize the frame to reduce processing load
        # frame = cv2.resize(frame, (640, 480))

        barcodes = decode(frame)
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            print(f"Detected barcode: {barcode_data}")

        # Lower the frame rate
        time.sleep(0.1)

    cap.release()


@app.get("/start")
async def start(background_tasks: BackgroundTasks):
    global camera_thread
    if camera_thread is None:
        camera_thread = threading.Thread(target=start_camera)
        background_tasks.add_task(camera_thread.start)
    return {"status": "Camera started"}


@app.get("/stop")
async def stop():
    global is_running, camera_thread
    is_running = False
    if camera_thread is not None:
        camera_thread.join()
        camera_thread = None
    return {"status": "Camera stopped"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
