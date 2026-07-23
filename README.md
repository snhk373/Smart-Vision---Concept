# Vision 视觉注入系统 / Vision Injection System

---

## 📖 中文介绍

### 项目简介
Vision 视觉注入系统是一套基于 Vulkan GPU 加速的实时计算机视觉处理平台，采用分体式多进程架构，支持摄像头画面采集、YOLO 姿态/目标检测、虚拟摄像头输出、窗口画面捕获、本地录制与开放 API 对接，可无缝接入腾讯会议、钉钉、OBS、直播伴侣等各类软件，适用于直播特效、线上会议、游戏辅助、动作追踪等多种场景。

### ✨ 核心特性
- **Vulkan GPU 加速渲染**：基于 Vulkan 计算管线实现图像预处理，降低 CPU 占用，提升实时处理帧率
- **多注入模式**：支持物理摄像头、虚拟摄像头、指定窗口捕获三种画面输入输出模式
- **双模式录制**：支持原始画面录制与 YOLO 叠加画面录制，一键切换
- **分体式架构**：启动画面、登录模块、主调度器、渲染引擎、功能子模块完全独立，单一模块崩溃不影响整体运行
- **标准化开放 API**：提供 MJPEG 直播流、录制控制、配置更新、目标追踪等 HTTP 接口，支持第三方软件二次开发
- **全场景兼容**：虚拟摄像头输出兼容所有识别普通摄像头的软件，无需额外插件

### 🏗️ 系统架构
项目采用模块化多进程设计，各模块独立运行、通过标准接口交互：
1. **启动引导模块**：可自定义时长的启动画面，支持品牌 Logo 与背景定制
2. **登录鉴权模块**：用户注册/登录、服务端地址配置、网络代理设置
3. **主调度面板**：统一功能入口，管理所有子进程生命周期，展示系统运行状态
4. **Vulkan 渲染后端**：常驻后台的 GPU 渲染与视觉计算引擎
5. **功能子模块**：摄像头录制、虚拟摄像头注入、窗口捕获注入
6. **服务端**：用户管理、设备上报、直播流分发、开放 API 服务

### 🎯 功能模块详解
#### 1. 摄像头预览与录制
- 实时采集物理摄像头画面
- 支持 YOLOv8 姿态关键点叠加显示
- 快捷键控制录制启停，支持原始/YOLO 双模式录制
- 自动按用户名与时间戳命名录像文件

#### 2. 虚拟摄像头注入
- 将处理后的画面输出到系统虚拟摄像头设备
- 支持姿态检测、目标检测两种叠加模式
- 兼容腾讯会议、钉钉、OBS、Zoom 等所有调用摄像头的软件
- 同步提供实时预览窗口

#### 3. 窗口捕获注入
- 枚举系统所有可见窗口，指定目标窗口实时捕获
- 支持游戏窗口、软件窗口的 YOLO 实时分析
- 可录制捕获画面，用于后期复盘与数据统计

#### 4. Vulkan 渲染后端
- 独立进程运行，不阻塞 GUI 界面响应
- 基于 Vulkan 计算队列实现 GPU 图像预处理
- 自动识别显卡设备，输出硬件信息日志

#### 5. 服务端开放 API
基于 FastAPI 构建的标准化接口服务：
- MJPEG 实时直播流：`/api/stream/live`
- 录制控制：开启/停止录制、查询录制状态
- 配置管理：远程更新 YOLO 模式、分辨率、帧率
- 目标追踪：设置追踪目标与平滑参数
- 设备管理：枚举系统可用摄像头设备

### 🚀 快速开始
#### 环境要求
- Windows 10 / 11
- Python 3.10+
- 支持 Vulkan 的独立显卡或核显
- （可选）OBS Studio（虚拟摄像头功能依赖其驱动）

#### 安装依赖
```bash
pip install opencv-python numpy ultralytics pillow requests pystray fastapi uvicorn pyvirtualcam pywin32 mss vulkan
```

#### 启动步骤
1. **启动服务端**
```bash
python server.py
```
服务默认监听 `0.0.0.0:8080`

2. **启动客户端**
```bash
python main_launcher.py
```
3. 注册账号并登录，在主面板选择对应功能即可使用

### 📦 打包部署
使用 PyInstaller 打包为独立可执行文件：
```bash
# 安装打包工具
pip install pyinstaller

# 打包主面板（无控制台窗口）
pyinstaller -D -w main_launcher.py -n Vision主面板

# 打包各功能子模块
pyinstaller -F render_backend.py -n Vulkan渲染后端
pyinstaller -F sub_camera.py -n 摄像头录制
pyinstaller -F virtual_cam_engine.py -n 虚拟摄像头注入
pyinstaller -F window_capture_engine.py -n 窗口捕获注入
pyinstaller -F server.py -n Vision服务端
```

### 📂 目录结构
```
P2/
├─ assets/                 # 启动画面资源文件
├─ log/                    # 运行日志目录
├─ record/                 # 录像文件保存目录
├─ user_data/              # 用户数据与配置
├─ main_launcher.py        # 主调度入口程序
├─ render_backend.py       # Vulkan 渲染后端
├─ sub_camera.py           # 摄像头预览录制模块
├─ virtual_cam_engine.py   # 虚拟摄像头注入模块
├─ window_capture_engine.py # 窗口捕获注入模块
└─ server.py               # 服务端与开放 API
```

### ⚠️ 注意事项
1. 虚拟摄像头功能需先安装 OBS Studio 并开启一次「虚拟摄像头」完成驱动注册
2. Vulkan 功能需确保显卡驱动已正确安装，调试建议安装 Vulkan SDK
3. 开放 API 对外访问需放行系统防火墙 8080 端口
4. YOLO 模型首次运行会自动下载，也可提前放置到程序同级目录

---

## 📖 English Introduction

### Project Overview
Vision Injection System is a real-time computer vision processing platform accelerated by Vulkan GPU. Built with a modular multi-process architecture, it supports camera capture, YOLO pose/object detection, virtual camera output, window capture, local recording and open API integration. It works seamlessly with Tencent Meeting, DingTalk, OBS Studio, live streaming tools and more, suitable for live effects, online conferences, game assistance, motion tracking and other scenarios.

### ✨ Core Features
- **Vulkan GPU Acceleration**: Image preprocessing based on the Vulkan compute pipeline reduces CPU usage and improves real-time processing framerate
- **Multiple Injection Modes**: Three input/output modes: physical camera, virtual camera and targeted window capture
- **Dual-Mode Recording**: Supports both raw footage and YOLO overlay recording, switchable with a single shortcut
- **Modular Architecture**: Splash screen, authentication, main launcher, render engine and sub-modules are fully independent; single module failure will not crash the whole system
- **Standard Open API**: Provides HTTP endpoints for MJPEG live stream, recording control, configuration updates and target tracking, enabling third-party integration
- **Universal Compatibility**: Virtual camera output works with all webcam-aware software without additional plugins

### 🏗️ System Architecture
The project follows a modular multi-process design. Each module runs independently and communicates through standard interfaces:
1. **Splash Module**: Customizable startup screen with brand logo and background support
2. **Authentication Module**: User registration/login, server configuration and network proxy settings
3. **Main Launcher Panel**: Unified function entry, manages lifecycle of all sub-processes and displays system status
4. **Vulkan Render Backend**: Background GPU rendering and visual computing engine
5. **Functional Sub-modules**: Camera recording, virtual camera injection, window capture injection
6. **Server Side**: User management, device reporting, live stream distribution and open API service

### 🎯 Feature Modules
#### 1. Camera Preview & Recording
- Real-time capture from physical cameras
- YOLOv8 pose keypoint overlay display
- Shortcut-controlled recording with raw/YOLO dual modes
- Auto-named video files by username and timestamp

#### 2. Virtual Camera Injection
- Outputs processed frames to the system virtual camera device
- Two overlay modes: pose detection and object detection
- Compatible with all camera-based software: Tencent Meeting, DingTalk, OBS, Zoom, etc.
- Synchronized real-time preview window

#### 3. Window Capture Injection
- Enumerates all visible system windows and captures the selected target in real time
- YOLO real-time analysis for game windows and application windows
- Recordable capture output for post-review and data analysis

#### 4. Vulkan Render Backend
- Runs in an independent process, does not block GUI responsiveness
- GPU image preprocessing via Vulkan compute queue
- Auto-detects GPU hardware and outputs device info logs

#### 5. Server Open API
Standard interface service built on FastAPI:
- MJPEG live stream: `/api/stream/live`
- Recording control: start/stop recording, query status
- Configuration management: remotely update YOLO mode, resolution, framerate
- Target tracking: set tracking target and smoothing parameters
- Device management: enumerate available system cameras

### 🚀 Quick Start
#### Requirements
- Windows 10 / 11
- Python 3.10+
- Discrete GPU or iGPU with Vulkan support
- (Optional) OBS Studio (required for virtual camera driver)

#### Install Dependencies
```bash
pip install opencv-python numpy ultralytics pillow requests pystray fastapi uvicorn pyvirtualcam pywin32 mss vulkan
```

#### Startup Steps
1. **Start the server**
```bash
python server.py
```
The service listens on `0.0.0.0:8080` by default.

2. **Start the client**
```bash
python main_launcher.py
```
3. Register an account, log in, and select features from the main panel.

### 📦 Packaging & Deployment
Package into standalone executables with PyInstaller:
```bash
# Install packaging tool
pip install pyinstaller

# Package main launcher (no console window)
pyinstaller -D -w main_launcher.py -n "Vision Launcher"

# Package functional modules
pyinstaller -F render_backend.py -n "Vulkan Render Backend"
pyinstaller -F sub_camera.py -n "Camera Recorder"
pyinstaller -F virtual_cam_engine.py -n "Virtual Camera Injector"
pyinstaller -F window_capture_engine.py -n "Window Capture"
pyinstaller -F server.py -n "Vision Server"
```

### 📂 Directory Structure
```
P2/
├─ assets/                 # Splash screen resources
├─ log/                    # Runtime logs
├─ record/                 # Recorded video files
├─ user_data/              # User data & configs
├─ main_launcher.py        # Main launcher entry
├─ render_backend.py       # Vulkan render backend
├─ sub_camera.py           # Camera preview & recording
├─ virtual_cam_engine.py   # Virtual camera injection
├─ window_capture_engine.py # Window capture injection
└─ server.py               # Server & open API
```

### ⚠️ Notes
1. Virtual camera requires OBS Studio installed; run "Start Virtual Camera" once to register the driver.
2. For Vulkan features, ensure your graphics driver is properly installed. Vulkan SDK is recommended for debugging.
3. Allow port 8080 in the system firewall for external API access.
4. YOLO models download automatically on first run; you can also pre-place them in the program directory.
