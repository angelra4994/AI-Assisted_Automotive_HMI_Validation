#!/usr/bin/env python3
"""Headless live USB-camera object detection with a YOLO TensorRT engine.

Designed for the Ultralytics JetPack 6 container where OpenCV is built with
GUI:NONE (no cv2.imshow). Frames are annotated and written to an output video
file; live FPS is printed to the console.

Run inside the container, e.g.:
    python3 live_detect.py --model /home/yolo/yolo26n.engine --source 0 \
        --imgsz 640 --out /home/yolo/live_out.mp4
"""
import argparse
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser(description="Headless live USB YOLO detection")
    p.add_argument("--model", default="/ultralytics/yolo26n.engine",
                   help="Path to the .engine (or .pt) model")
    p.add_argument("--source", default="0",
                   help="Camera index (e.g. 0) or /dev/videoN path")
    p.add_argument("--imgsz", type=int, default=640, help="Inference size")
    p.add_argument("--cap-width", type=int, default=1280, help="Capture width")
    p.add_argument("--cap-height", type=int, default=720, help="Capture height")
    p.add_argument("--cap-fps", type=int, default=30, help="Requested camera FPS")
    p.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    p.add_argument("--out", default="/home/yolo/live_out.mp4",
                   help="Annotated output video path")
    p.add_argument("--max-frames", type=int, default=0,
                   help="Stop after N frames (0 = run until Ctrl+C)")
    p.add_argument("--stream", action="store_true",
                   help="Serve an MJPEG stream over HTTP for remote viewing")
    p.add_argument("--host", default="0.0.0.0", help="Stream bind address")
    p.add_argument("--port", type=int, default=8090, help="Stream HTTP port")
    p.add_argument("--no-save", action="store_true",
                   help="Do not write the annotated output video file")
    p.add_argument("--task", default=None,
                   choices=["detect", "segment", "classify", "pose", "obb"],
                   help="Override task; omit to auto-detect from the engine metadata")
    return p.parse_args()


def open_camera(source, width, height, fps):
    # Prefer the V4L2 backend explicitly; on Jetson it is the reliable path.
    idx = int(source) if str(source).isdigit() else source
    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
    if not cap.isOpened():
        raise RuntimeError(
            f"Cannot open camera '{source}'. Check --device mapping and /dev/video*"
        )
    # MJPEG lets most USB webcams deliver full FPS at higher resolutions
    # (raw YUYV is bandwidth-limited and often drops to ~5 FPS at 720p).
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # minimize latency; always use freshest frame
    return cap


class MjpegStreamer:
    """Serves the latest annotated frame as MJPEG over HTTP.

    View in any browser at http://<jetson-ip>:<port>/ . Works headlessly
    (no OpenCV GUI or GStreamer needed) via multipart/x-mixed-replace.
    """

    def __init__(self, host="0.0.0.0", port=8090):
        self._cond = threading.Condition()
        self._jpeg = None
        streamer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass  # silence per-request logging

            def do_GET(self):
                if self.path not in ("/", "/stream", "/stream.mjpg"):
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "multipart/x-mixed-replace; boundary=frame",
                )
                self.end_headers()
                try:
                    while True:
                        with streamer._cond:
                            streamer._cond.wait(timeout=5.0)
                            frame = streamer._jpeg
                        if frame is None:
                            continue
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n")
                        self.wfile.write(
                            f"Content-Length: {len(frame)}\r\n\r\n".encode()
                        )
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                except (BrokenPipeError, ConnectionResetError):
                    pass  # client disconnected

        self._server = ThreadingHTTPServer((host, port), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True
        )

    def start(self):
        self._thread.start()

    def update(self, jpeg_bytes):
        with self._cond:
            self._jpeg = jpeg_bytes
            self._cond.notify_all()

    def stop(self):
        self._server.shutdown()
        self._server.server_close()


def main():
    args = parse_args()

    print(f"[init] loading model: {args.model}")
    model = YOLO(args.model, task=args.task)  # task auto-detected from engine if None

    cap = open_camera(args.source, args.cap_width, args.cap_height, args.cap_fps)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    if not actual_fps or actual_fps <= 0:
        actual_fps = args.cap_fps  # many MJPEG USB cams report 0; fall back
    print(f"[cam ] {actual_w}x{actual_h} @ {actual_fps:.0f} FPS (requested)")

    writer = None
    if not args.no_save:
        writer = cv2.VideoWriter(
            args.out, cv2.VideoWriter_fourcc(*"mp4v"),
            max(actual_fps, 15), (actual_w, actual_h),
        )
        if not writer.isOpened():
            raise RuntimeError(f"Cannot open VideoWriter for '{args.out}'")

    streamer = None
    if args.stream:
        streamer = MjpegStreamer(args.host, args.port)
        streamer.start()
        print(f"[strm] MJPEG live view at http://<jetson-ip>:{args.port}/")

    # Warmup: the first TensorRT inferences allocate buffers and are slow.
    print("[warm] warming up engine...")
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Camera opened but returned no frame")
    for _ in range(5):
        model.predict(frame, imgsz=args.imgsz, conf=args.conf, verbose=False)

    fps_window = deque(maxlen=30)
    frame_count = 0
    print("[run ] streaming... Ctrl+C to stop")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[warn] dropped frame")
                continue

            t0 = time.perf_counter()
            results = model.predict(
                frame, imgsz=args.imgsz, conf=args.conf, verbose=False
            )
            dt = time.perf_counter() - t0
            fps_window.append(1.0 / dt if dt > 0 else 0.0)

            annotated = results[0].plot()
            fps = sum(fps_window) / len(fps_window)
            cv2.putText(
                annotated, f"{fps:.1f} FPS", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2,
            )
            if writer is not None:
                writer.write(annotated)
            if streamer is not None:
                ok_enc, buf = cv2.imencode(
                    ".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80]
                )
                if ok_enc:
                    streamer.update(buf.tobytes())

            frame_count += 1
            if frame_count % 30 == 0:
                print(f"[fps ] {fps:6.1f}  (inference {dt * 1000:5.1f} ms)")
            if args.max_frames and frame_count >= args.max_frames:
                break
    except KeyboardInterrupt:
        print("\n[stop] interrupted by user")
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        if streamer is not None:
            streamer.stop()
        print(f"[done] {frame_count} frames processed")


if __name__ == "__main__":
    main()
