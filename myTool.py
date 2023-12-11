import time
import network
from machine import RTC
from math import ceil

# 显示字符（中英文皆可）,取模方式为列行式
def display_text(tft,pos,text,color,font):
    for ch in range(len(text)):
        fontw = font["Width"]
        fonth = font["Height"]
        countw = ceil(fontw/8)# 表示有几组行
        counth = ceil(fonth/8) # 表示有几组列
        charData = bytearray(font["Data"][text[ch]])
        buf = bytearray(2 *fonth * fontw)
        parts=[]
        for numh in range(1,counth+1):
            parts.append(charData[(8*countw)*(numh-1):(8*countw) * numh])
            for q in range(fontw):
                c = parts[numh-1][q]
                for numw in range(1,countw+1):
                    for r in range((8*numw)*(numh-1),(8*numw) * numh):
                        if c & 0x01:
                            coordinate = 2*(r * fontw + q)
                            buf[coordinate] = color >> 8
                            buf[coordinate + 1] = color & 0xFF
                        c >>= 1
        tft.image(pos[0]+fontw*ch+1, pos[1], (pos[0]+fontw*ch+1) + fontw - 1, pos[1] + fonth - 1, buf)

# 显示图片
def display_img(tft,pos,size,img):
    with open(img, "rb") as f:
        for row in range(size[1]): 
            buffer = f.read(size[0]*2)
            tft.image(pos[0], row+pos[1], size[0]+pos[0], row+pos[1], buffer)


# 连接wifi
def wifi_connect(ssid, password):
    # 创建 WIFI 连接对象
    wlan = network.WLAN(network.STA_IF)
    # 激活 wlan 接口
    wlan.active(True)

    if not wlan.isconnected():
        wlan.connect(ssid, password)
        i = 1
        # 如果一直没有连接成功，则每隔 0.1s 在命令号中打印一个 .
        while not wlan.isconnected():
          print("正在连接.", end="")
          i+=1
          time.sleep(1)
          
# 通过ntp进行时间校准
def sync_ntp():
    """通过网络校准时间"""
    import ntptime
    ntptime.NTP_DELTA = 3155644800
    ntptime.host = 'ntp1.aliyun.com'
    while True:   #时间校准
        try:
            print('time ing')
            ntptime.settime()
            print('time ok')
            break;
        except:
            print('time no')
            time.sleep(1)

# 更新时间的方法
def update_time():
    rtc = RTC()
    week=("周一","周二","周三","周四","周五","周六","周日")
    nowTime = rtc.datetime()
    date = "%02d-%02d" %(nowTime[1],nowTime[2])
    time = "%02d:%02d" % (nowTime[4],nowTime[5])
    week = week[nowTime[3]]
    return date,time,week
# 计算时间差
def countdownDay(date_str1,tft,font):
    rtc = RTC()
    nowTime = rtc.datetime()
    nowDate = "%04d-%02d-%02d" %(nowTime[0],nowTime[1],nowTime[2])
    # 将日期字符串拆分为年、月、日
    year1, month1, day1 = map(int, date_str1.split("-"))
    
    display_text(tft,(24,15),"在一起已经",tft.WHITE,font)
    display_text(tft,(54,100),"天",tft.WHITE,font)
    # 计算时间差（以天为单位）
    time_diff = str((nowTime[0] - year1) * 365 + (nowTime[1] - month1) * 30 + (nowTime[2] - day1))
    for i in range(len(time_diff)):
        # 图片的尺寸为：28*55
        if i == 0:
            display_img(tft,(24,40),(28,55),"/imgs/numy"+str(time_diff[i])+".dat")
        else:
            display_img(tft,(24+28*i,40),(28,55),"/imgs/num"+str(time_diff[i])+".dat")

