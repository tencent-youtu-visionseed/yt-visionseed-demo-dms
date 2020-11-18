# yt-visionseed-demo-dms
## 此示例为用VisionSeed做的检测疲劳驾驶的程序

## 安装visionseed库

```python
pip3 install --upgrade visionseed
```

## 安装依赖库，运行 main.py
```python
pip3 install opencv-python
pip3 install numpy
pip3 install serial
pip3 install pygame
pip3 install collection
python3 main.py
```

在windows上运行示例程序，需要修改example.py中连接端口的代码，并将“/dev/ttyACM0”替换为VisionSeed的虚拟端口号，例如“COM3”：

```python
vs = YtVisionSeed(serial.Serial("/dev/ttyACM0",115200,timeout=0.5))
```
