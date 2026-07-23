import cv2
import numpy as np
from ultralytics import YOLO
import sys
import os
from datetime import datetime

RECORD_DIR = "./record"
os.makedirs(RECORD_DIR, exist_ok=True)

args_dict = {}
for a in sys.argv[1:]:
    if a.startswith("--"):
        k, v = a.lstrip("--").split("=", 1)
        args_dict[k] = v

user = args_dict.get("user", "guest")
w, h = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

# 加载姿态检测模型
model = YOLO("yolov8n-pose.pt", verbose=False)
yolo_overlay = True  # 默认开启YOLO叠加
recording = False
out = None
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
win_name = "摄像头 [R录制 Y切换YOLO ESC退出]"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win_name, w, h)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    display_frame = frame.copy()

    # YOLO骨骼点叠加
    if yolo_overlay:
        res = model(frame, pose=True, verbose=False)[0]
        if res.keypoints is not None:
            for p in res.keypoints.data.cpu().numpy():
                for x, y, c in p:
                    if c > 0.5:
                        cv2.circle(display_frame, (int(x), int(y)), 3, (0, 255, 0), -1)

    # 状态提示文字
    mode_text = "YOLO录制" if (recording and yolo_overlay) else ("原始录制" if recording else "预览中")
    cv2.putText(display_frame, f"User:{user} | {mode_text}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    if recording and out:
        # 区分原始/YOLO录制输出
        out.write(display_frame if yolo_overlay else frame)

    cv2.imshow(win_name, display_frame)
    k = cv2.waitKey(1) & 0xFF
    if k == ord("r") or k == ord("R"):
        recording = not recording
        if recording:
            fn = os.path.join(RECORD_DIR,
                f"{user}_{'yolo_' if yolo_overlay else 'raw_'}{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            out = cv2.VideoWriter(fn, fourcc, 24, (w, h))
            print(f"开始录制: {fn}")
        else:
            if out:
                out.release()
                out = None
            print("停止录制")
    elif k == ord("y") or k == ord("Y"):
        yolo_overlay = not yolo_overlay
        print(f"YOLO叠加: {'开启' if yolo_overlay else '关闭'}")
    elif k == 27:
        break

cap.release()
if out:
    out.release()
cv2.destroyAllWindows()
