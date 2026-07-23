import cv2
import numpy as np
import mss
import win32gui
from ultralytics import YOLO
import sys
import time
import os

args = {}
for a in sys.argv[1:]:
    if a.startswith("--"):
        k, v = a.lstrip("--").split("=", 1)
        args[k] = v

YOLO_ENABLE = args.get("yolo", "1") == "1"
POSE_MODE = args.get("mode", "pose") == "pose"
RECORD_ENABLE = args.get("record", "0") == "1"
RECORD_PATH = args.get("rec_path", "./record")
os.makedirs(RECORD_PATH, exist_ok=True)

# 枚举系统所有可见窗口
def enum_windows():
    wins = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            title = win32gui.GetWindowText(hwnd)
            wins.append((hwnd, title))
        return True
    win32gui.EnumWindows(callback, None)
    return wins

def select_window():
    wins = enum_windows()
    print("=== 可用窗口列表 ===")
    for i, (hwnd, title) in enumerate(wins):
        print(f"[{i}] {title}")
    idx = int(input("请输入窗口编号: "))
    return wins[idx][0]

def main():
    hwnd = select_window()
    if not hwnd:
        return
    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    print(f"[捕获] 窗口尺寸: {w}x{h}")

    # 加载YOLO模型
    model = None
    if YOLO_ENABLE:
        model_name = "yolov8n-pose.pt" if POSE_MODE else "yolov8n.pt"
        model = YOLO(model_name, verbose=False)

    # 录制初始化
    writer = None
    if RECORD_ENABLE:
        fn = os.path.join(RECORD_PATH, f"window_capture_{int(time.time())}.mp4")
        writer = cv2.VideoWriter(fn, cv2.VideoWriter_fourcc(*"mp4v"), 24, (w, h))
        print(f"[录制] 保存到: {fn}")

    sct = mss.mss()
    monitor = {"top": rect[1], "left": rect[0], "width": w, "height": h}
    cv2.namedWindow("窗口捕获注入 [ESC退出]", cv2.WINDOW_NORMAL)

    while True:
        if not win32gui.IsWindow(hwnd):
            print("[错误] 目标窗口已关闭")
            break
        # 高速捕获窗口画面
        img = sct.grab(monitor)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # YOLO叠加处理
        if YOLO_ENABLE and model:
            result = model(frame, verbose=False)[0]
            if POSE_MODE and result.keypoints is not None:
                for person in result.keypoints.data.cpu().numpy():
                    for x, y, c in person:
                        if c > 0.5:
                            cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 0), -1)
            elif not POSE_MODE and result.boxes is not None:
                for box in result.boxes:
                    x1,y1,x2,y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

        if writer:
            writer.write(frame)
        cv2.imshow("窗口捕获注入 [ESC退出]", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    if writer:
        writer.release()
    cv2.destroyAllWindows()
    print("[退出] 窗口捕获结束")

if __name__ == "__main__":
    main()
