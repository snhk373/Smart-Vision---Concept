import vulkan as vk
import cv2
import numpy as np
from ultralytics import YOLO
import sys
import time
import os
from datetime import datetime
import logging

args_dict = {}
for arg in sys.argv[1:]:
    if arg.startswith("--"):
        k, v = arg.lstrip("--").split("=", 1)
        args_dict[k] = v

CAM_ID = int(args_dict.get("cam", 0))
WIN_W = int(args_dict.get("width", 1280))
WIN_H = int(args_dict.get("height", 720))
CUR_USER = args_dict.get("user")
RECORD_FOLDER = "./record"
os.makedirs(RECORD_FOLDER)
logging.basicConfig(level=logging.INFO, format="[Vulkan] %(asctime)s | %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("VulkanEngine")
logger.info("Vulkan渲染后端启动")

def init_vulkan():
    app_info = vk.VkApplicationInfo(pApplicationName="Vision", applicationVersion=vk.VK_MAKE_VERSION(1,0,0), apiVersion=vk.VK_API_VERSION_1_1)
    inst = vk.vkCreateInstance(vk.VkInstanceCreateInfo(pApplicationInfo=app_info), None)
    phys = vk.vkEnumeratePhysicalDevices(inst)[0]
    dev_prop = vk.vkGetPhysicalDeviceProperties(phys)
    logger.info(f"GPU:{dev_prop.deviceName.decode()}")
    q_fams = vk.vkGetPhysicalDeviceQueueFamilyProperties(phys)
    q_idx = 0
    for i,f in enumerate(q_fams):
        if f.queueFlags & vk.VK_QUEUE_COMPUTE_BIT:
            q_idx = i
            break
    q_info = vk.VkDeviceQueueCreateInfo(queueFamilyIndex=q_idx, queueCount=1, pQueuePriorities=[1.0])
    dev = vk.vkCreateDevice(phys, vk.VkDeviceCreateInfo(queueCreateInfoCount=1, pQueueCreateInfos=[q_info]), None)
    q = vk.vkGetDeviceQueue(dev, q_idx, 0)
    cmd_pool = vk.vkCreateCommandPool(dev, vk.VkCommandPoolCreateInfo(queueFamilyIndex=q_idx), None)
    return inst, dev, q, cmd_pool

def main():
    inst, dev, q, pool = init_vulkan()
    model = YOLO("yolov8n-pose", verbose=False)
    cap = cv2.VideoCapture(CAM_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIN_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WIN_H)
    if not cap.isOpened():
        logger.error("摄像头打开失败")
        return
    cv2.namedWindow("Vulkan后端流", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Vulkan后端流", WIN_W, WIN_H)
    fps_cnt = 0
    last_t = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        res = model(frame, pose=True)[0]
        if res.keypoints is not None:
            kps = res.keypoints.data.cpu().numpy()
            for person in kps:
                for x,y,c in person:
                    if c>0.5:
                        cv2.circle(frame, (int(x),int(y)),3,(0,255,0),-1)
        fps_cnt +=1
        if time.time() - last_t >=1:
            cv2.putText(frame, f"FPS:{fps_cnt}", (10,30), cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
            fps_cnt=0
            last_t=time.time()
        cv2.imshow("Vulkan后端流", frame)
        if cv2.waitKey(1)&0xFF ==27:
            break
    cap.release()
    cv2.destroyAllWindows()
    vk.vkDestroyCommandPool(dev, pool, None)
    vk.vkDestroyDevice(dev, None)
    vk.vkDestroyInstance(inst, None)
    logger.info("渲染后端退出")

if __name__ == "__main__":
    main()
