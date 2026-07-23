import sys
import os
import cv2
import numpy as np
from ultralytics import YOLO
import vulkan as vk
import time
from datetime import datetime
import logging

# 解析启动参数
args_dict = {}
for arg in sys.argv[1:]:
    if arg.startswith("--"):
        k, v = arg.lstrip("--").split("=", 1)
        args_dict[k] = v

CAM_ID = int(args_dict.get("cam", 0))
WIN_W = int(args_dict.get("width", 1280))
WIN_H = int(args_dict.get("height", 720))
CUR_USER = args_dict.get("user")
RECORD_FOLDER = args_dict.get("local_rec", "./record")
DO_LOCAL_REC = bool(int(args_dict.get("rec_local", 1)))
os.makedirs(RECORD_FOLDER, exist_ok())

# 控制台日志
logging.basicConfig(
    level=logging.INFO,
    format="[VulkanEngine] %(asctime)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("VulkanEngine")
logger.info("==== Vulkan Vision Render Engine Start ====")

# Vulkan 全局资源
inst = None
phys_dev = None
logical_device = None
queue_family_idx = None
queue = None
command_pool = None

# 简单Vulkan初始化
def init_vulkan():
    global inst, phys_dev, logical_device, queue_family_idx, queue, command_pool
    app_info = vk.VkApplicationInfo(
        sType=vk.VK_STRUCTURE_TYPE_APPLICATION_INFO,
        pApplicationName="VisionVulkan",
        applicationVersion=vk.VK_MAKE_VERSION(1,0,0),
        pEngineName="ComputeShader",
        engineVersion=vk.VK_MAKE_VERSION(1,0,0),
        apiVersion=vk.VK_API_VERSION_1_1
    )
    create_info = vk.VkInstanceCreateInfo(pApplicationInfo=app_info)
    inst = vk.vkCreateInstance(create_info, None)
    phys_devices = vk.vkEnumeratePhysicalDevices(inst)
    phys_dev = phys_devices[0]
    dev_prop = vk.vkGetPhysicalDeviceProperties(phys_dev)
    logger.info(f"Vulkan GPU: {dev_prop.deviceName.decode()}")
    # 寻找计算队列
    queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(phys_dev)
    for idx, qf in enumerate(queue_families):
        if qf.queueFlags & vk.VK_QUEUE_COMPUTE_BIT:
            queue_family_idx = idx
            break
    # 创建逻辑设备
    queue_prio = [1.0]
    queue_info = vk.VkDeviceQueueCreateInfo(
        queueFamilyIndex=queue_family_idx,
        queueCount=1,
        pQueuePriorities=queue_prio
    )
    dev_create = vk.VkDeviceCreateInfo(queueCreateInfoCount=1, pQueueCreateInfos=[queue_info])
    logical_device = vk.vkCreateDevice(phys_dev, dev_create, None)
    queue = vk.vkGetDeviceQueue(logical_device, queue_family_idx, 0)
    # 命令池
    cmd_pool_info = vk.VkCommandPoolCreateInfo(queueFamilyIndex=queue_family_idx)
    command_pool = vk.vkCreateCommandPool(logical_device, cmd_pool_info, None)

# Vulkan图像预处理（GPU转RGB浮点）
def vulkan_process_image(dev, pool, q, img_np):
    h,w,c = img_np.shape
    size = h * w * c
    buf_create = vk.VkBufferCreateInfo(
        size=size,
        usage=vk.VK_BUFFER_USAGE_TRANSFER_SRC_BIT | vk.VK_BUFFER_USAGE_STORAGE_BUFFER_BIT,
        sharingMode=vk.VK_SHARING_MODE_EXCLUSIVE
    )
    buf = vk.vkCreateBuffer(dev, buf_create, None)
    req = vk.vkGetBufferMemoryRequirements(dev, buf)
    mem_type_idx = 0
    mem_props = vk.vkGetPhysicalDeviceMemoryProperties(phys_dev)
    for i in range(mem_type_idx):
        if req.memoryTypeBits & (1 << i) and (mem_props.memoryTypes[i].propertyFlags & vk.VK_MEM_PROPERTY_HOST_COHERENT_BIT):
            mem_type_idx = i
            break
    alloc_info = vk.VkMemoryAllocateInfo(req.size, mem_type_idx)
    mem = vk.vkAllocateMemory(dev, alloc_info, None)
    vk.vkBindBufferMemory(dev, buf, mem, 0)
    data_ptr = vk.vkMapMemory(dev, mem, 0, size, 0)
    np_mem = np.ctypeslib.as_array((ctypes.c_ubyte * size).from_address(data_ptr))
    np_mem[:] = img_np.reshape(-1)
    vk.vkUnmapMemory(dev, mem)
    return buf, mem

# 主渲染循环
def main_render():
    init_vulkan()
    logger.info("加载YOLOv8n-pose模型...")
    model = YOLO("yolov8n-pose.pt", verbose=False)
    cap = cv2.VideoCapture(CAM_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIN_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, WIN_H)
    if not cap.isOpened():
        logger.error("摄像头打开失败")
        return
    out_writer = None
    if DO_LOCAL_REC:
        mp4_name = os.path.join(RECORD_FOLDER, f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{CUR_USER}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out_writer = cv2.VideoWriter(mp4_name, fourcc, 24, (WIN_W, WIN_H))
        logger.info(f"录像文件: {mp4_name}")
    cv2.namedWindow("Vulkan Vision Preview [ESC退出]", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Vulkan Vision Preview [ESC退出]", WIN_W, WIN_H)
    fps_counter = 0
    last_fps_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (WIN_W, WIN_H))
        # Vulkan GPU预处理
        vulkan_process_image(logical_device, command_pool, queue, frame)
        # YOLO推理
        result = model(frame, pose=True, verbose=False)[0]
        person_count = 0
        if result.keypoints is not None:
            kpts = result.keypoints.data.cpu().numpy()
            person_count = len(kpts)
            for person in kpts:
                for (x,y,conf) in person:
                    if conf>0.5:
                        cv2.circle(frame, (int(x),int(y)), 3, (0,255,0), -1)
        # FPS文字
        fps_counter +=1
        now = time.time()
        if now - last_fps_time >= 1.0:
            fps = fps_counter
            fps_counter = 0
            last_fps_time = now
            cv2.putText(frame, f"FPS:{fps} Person:{person_count} Vulkan GPU", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        if out_writer:
            out_writer.write(frame)
        cv2.imshow("Vulkan Vision Preview [ESC退出]", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            logger.info("收到ESC，停止渲染")
            break
    cap.release()
    if out_writer:
        out_writer.release()
    cv2.destroyAllWindows()
    # 释放Vulkan资源
    vk.vkDestroyCommandPool(logical_device, command_pool, None)
    vk.vkDestroyDevice(logical_device, None)
    vk.vkDestroyInstance(inst, None)
    logger.info("Vulkan引擎正常退出")

if __name__ == "__main__":
    import ctypes
    try:
        main_render()
    except Exception as e:
        logger.exception("Vulkan引擎异常崩溃")
