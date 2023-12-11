from machine import SPI, Pin, Timer
from ST7735 import TFT
import random
import time
from myFont import *
from myTool import *
from math import ceil
from weather import *
from MQTT import MQTTClient

ssid = "wifi名"
password = "wifi密码"

clientId = "本机客户端ID"
startDay = ""  # 在一起的日子 格式YYYY-MM-DD
sendTo = b"发送方客户端的ID"
reciviceFrom = b"接收方客户端的ID"
# 保存按键按下的状态，
status = 0
# 保存上一次按键按下的状态
lastStatus = 0
# 记录按键按下的时间，判断是否长按
current_time = 0
last_time = 0

lock = 0
isLongPress = False

spi = SPI(2, baudrate=40000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=None)
tft = TFT(spi, 2, 4, 5)
tft.initr()
tft.rgb(False)
tft.fill(TFT.BLACK)

# 定义按键引脚,另一端接地，设置为上拉电阻
button = Pin(33, Pin.IN, Pin.PULL_UP)

# 旋转屏幕
tft.rotation(3)
imgNum = 1

timer = Timer(0)
timer_water = Timer(1)
c1 = None


# 开机时初始化各项数据
def initData():
    global c1
    wifi_connect(ssid, password)
    update_weather()
    tft.fill(TFT.BLACK)
    sync_ntp()
    timer.init(mode=Timer.PERIODIC, period=1000,
               callback=showNowDate)  # 初始化一个mqtt客户端
    c1 = MQTTClient(clientId, "192.168.31.238")  # 建立一个MQTT客户端
    c1.set_callback(sub_cb)  # 设置回调函数
    c1.connect(True)  # 建立连接
    c1.subscribe(sendTo)  # 监控ledctl这个通道，接收控制命令

# 定时早上好


def goodMorning():
    tft.fill(TFT.BLACK)
    timer.deinit()
    count = 0
    imgNum = 1
    display_text(tft, (23, 40), "宝宝早上好~", tft.WHITE, full_angle_16)
    while count < 60:
        display_img(tft, (5, 80), (32, 32), "imgs/rabit_"+str(imgNum)+".dat")
        imgNum += 1
        count += 1
        if imgNum == 4:
            imgNum = 1
        time.sleep(1)

    tft.fill(TFT.BLACK)
    timer.init(mode=Timer.PERIODIC, period=1000, callback=showNowDate)


# 展示时间,定时器用
def showNowDate(timer_obj):
    global imgNum
    nowDate, nowTime, nowWeek = update_time()
    # 将两个图像合并
    display_img(tft, (0, 0), (64, 40), "/imgs/bg_1.dat")
    display_img(tft, (64, 33), (64, 7), "/imgs/bg_2.dat")
    weatherId = display_today()
    display_img(tft, (90, 0), (32, 32), "/imgs/img" +
                weatherId+"_"+str(imgNum)+".dat")
    imgNum += 1
    if imgNum == 3:
        imgNum = 1
    display_text(tft, (5, 50), nowTime, tft.WHITE, half_angle_48)
    tft.line((5, 100), (125, 100), tft.WHITE)
    display_text(tft, (20, 105), nowDate, tft.WHITE, half_angle_16)
    display_text(tft, (80, 105), nowWeek, tft.WHITE, full_angle_16)

# 回调函数，收到服务器消息后会调用这个函数


def sub_cb(topic, msg):
    if topic != None:
        # 显示一张爱你的图片；
        timer.deinit()
        tft.fill(TFT.BLACK)
        count = 0
        while count < 40:
            for i in range(1, 5):
                display_img(tft, (30, 30), (64, 64),
                            "/imgs/heart"+str(i)+".dat")
                time.sleep(0.5)
            count += 1
        tft.fill(TFT.BLACK)
        timer.init(mode=Timer.PERIODIC, period=1000, callback=showNowDate)


initData()

while True:
    nowDate, nowTime, nowWeek = update_time()

    # 持续监听是否有消息收到
    c1.check_msg()
    if nowTime == "8:40":
        goodMorning()
    # 按键模块
    if button.value() == 0:
        time.sleep_ms(10)  # 延时10ms，消除按键抖动
        current_time = time.time()

        # 长按
        if button.value() == 0 and lock == 0:
            last_time = time.time()
            lock = 1

        # 单击切换
        if button.value() == 0:
            if current_time - last_time > 2 and lock == 1:
                c1.publish(reciviceFrom, "11")
                lock = 0
                isLongPress = True
        if button.value() == 1:
            lock = 0
            if isLongPress:
                isLongPress = False
            else:
                print(status)
                # 松开按键后轮流切换屏幕画面显示
                if status == 0:
                    timer.deinit()
                    display_4d(tft)
                elif status == 1:
                    tft.fill(TFT.BLACK)
                    countdownDay(startDay, tft, full_angle_16)
                elif status == 2:
                    tft.fill(TFT.BLACK)
                    timer.init(mode=Timer.PERIODIC, period=1000,
                               callback=showNowDate)

                status += 1
                if status == 3:
                    status = 0
