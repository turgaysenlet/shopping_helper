import os
import cv2
import threading
import time
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pyzbar.pyzbar import decode

app = FastAPI()

# Configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

camera_thread = None
is_running = False
latest_barcode = ""


def start_camera():
    global is_running, latest_barcode
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
        frame = cv2.resize(frame, (640, 480))

        barcodes = decode(frame)
        for barcode in barcodes:
            latest_barcode = barcode.data.decode('utf-8')
            print(f"Detected barcode: {latest_barcode}")

        time.sleep(0.1)

    cap.release()


@app.get("/")
async def index():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Barcode Scanner</title>
        <style>
            #video {
                width: 640px;
                height: 480px;
                border: 1px solid black;
            }
        </style>
    </head>
    <body>
        <h1>Barcode Scanner</h1>
        <video id="video" autoplay></video>
        <h2>Latest Barcode: <span id="barcode"></span></h2>
        <button onclick="startCamera()">Start Camera</button>
        <button onclick="stopCamera()">Stop Camera</button>
        <script>
            let video = document.getElementById('video');
            let barcodeElement = document.getElementById('barcode');
            let stream;

            async function startCamera() {
                let response = await fetch('/start');
                let result = await response.json();
                console.log(result);

                if (navigator.mediaDevices.getUserMedia) {
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    video.srcObject = stream;
                }

                // Fetch the latest barcode periodically
                setInterval(async () => {
                    let barcodeResponse = await fetch('/barcode');
                    let barcodeResult = await barcodeResponse.json();
                    barcodeElement.textContent = barcodeResult.barcode;
                }, 1000);
            }

            async function stopCamera() {
                let response = await fetch('/stop');
                let result = await response.json();
                console.log(result);

                if (stream) {
                    let tracks = stream.getTracks();
                    tracks.forEach(track => track.stop());
                    video.srcObject = null;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


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


@app.get("/barcode")
async def get_barcode():
    global latest_barcode
    return {"barcode": latest_barcode}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
