import cv2
import numpy as np
import pyvirtualcam
from ultralytics import YOLO
import sys
import time
import os

# 解析命令行参数
args = {}
for a in sys.argv[1:]:
    if a.startswith("--"):
        k, v = a.lstrip("--").split("=", 1)
        args[k] = v

CAM_ID = int(args.get("cam", 0))
WIDTH = int(args.get("width", 1280))
HEIGHT = int(args.get("height", 720))
FPS = int(args.get("fps", 30))
YOLO_ENABLE = args.get("yolo", "1") == "1"
POSE_MODE = args.get("mode", "pose") == "pose"

def main():
    # 打开物理摄像头
    cap = cv2.VideoCapture(CAM_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)
    if not cap.isOpened():
        print("[错误] 物理摄像头打开失败")
        return

    # 加载YOLO模型
    model = None
    if YOLO_ENABLE:
        model_name = "yolov8n-pose.pt" if POSE_MODE else "yolov8n.pt"
        print(f"[加载] YOLO模型: {model_name}")
        model = YOLO(model_name, verbose=False)

    # 启动虚拟摄像头
    try:
        with pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS) as cam:
            print(f"[就绪] 虚拟摄像头已启动: {WIDTH}x{HEIGHT} @ {FPS}fps")
            print("[提示] 第三方软件选择「OBS Virtual Camera」即可看到注入画面，ESC退出")
            cv2.namedWindow("虚拟摄像头预览 [ESC退出]", cv2.WINDOW_NORMAL)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.resize(frame, (WIDTH, HEIGHT))

                # YOLO画面处理
                if YOLO_ENABLE and model:
                    result = model(frame, verbose=False)[0]
                    if POSE_MODE and result.keypoints is not None:
                        kpts = result.keypoints.data.cpu().numpy()
                        for person in kpts:
                            for x, y, conf in person:
                                if conf > 0.5:
                                    cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 0), -1)
                    elif not POSE_MODE and result.boxes is not None:
                        for box in result.boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 输出到虚拟摄像头（需RGB格式）
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cam.send(frame_rgb)
                cam.sleep_until_next_frame()

                cv2.imshow("虚拟摄像头预览 [ESC退出]", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
    except Exception as e:
        print(f"[错误] 虚拟摄像头启动失败: {e}")
        print("请先安装OBS Studio并启动一次虚拟摄像头完成驱动注册")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[退出] 虚拟摄像头已关闭")

if __name__ == "__main__":
    main()
