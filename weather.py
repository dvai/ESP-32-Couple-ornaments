import ujson
import urequests
import uzlib as zlib
from myTool import *
from myFont import half_angle_16
ssid = "vaifix"
password = "827427325"

# 保存4日天气数据
weatherDic = {}
imgs = ["晴", "多云", "雾", "雷", "阴", "雨", "雪", "大雨"]
# 天气数据解包


def decompress(data):
    assert data[0] == 0x1f and data[1] == 0x8b
    assert data[2] == 8
    flg = data[3]
    assert flg & 0xe0 == 0
    i = 10
    if flg & 4:
        i += data[11] << 8 + data[10] + 2
    if flg & 8:
        while data[i]:
            i += 1
        i += 1
    if flg & 16:
        while data[i]:
            i += 1
        i += 1
    if flg & 2:
        i += 2
    return zlib.decompress(memoryview(data)[i:], -15)

# 更新天气


def update_weather():
    global weatherDic
    url = '和风天气API地址'  # 7日天气预告
    res = urequests.get(url)
    data = decompress(res.content).decode()
    dic = ujson.loads(data)

    for i in range(4):
        weatherDic[i] = [dic["daily"][i]["textDay"], dic["daily"]
                         [i]["tempMax"], dic["daily"][i]["tempMin"]]

# 显示今日天气


def display_today():
    todayWeather = weatherDic[0][0]
    for i in range(len(imgs)-1, -1, -1):
        if imgs[i] in todayWeather:
            return str(i+1)

# 显示4日天气


def display_4d(tft):
    tft.fill(tft.BLACK)
    update_weather()
    maxT = int(max(weatherDic[0][1], weatherDic[1]
               [1], weatherDic[2][1], weatherDic[3][1]))
    minT = int(min(weatherDic[0][2], weatherDic[1]
               [2], weatherDic[2][2], weatherDic[3][2]))
    rate = 40/(maxT-minT)
    for i in range(4):
        weatherid = 0
        for j in range(len(imgs)-1, -1, -1):
            if imgs[j] in weatherDic[i][0]:
                weatherid = j+1
                break
        display_img(tft, (0+32*i, 10), (32, 32),
                    "imgs/img"+str(weatherid)+"_1.dat")
        # 折线图
        if i < 3:
            tft.line((16+32*i, 60+int(rate*(maxT-int(weatherDic[i][1])))), (48+32*i, 60+int(
                rate*(maxT-int(weatherDic[i+1][1])))), tft.WHITE)
            tft.line((16+32*i, 60+int(rate*(maxT-int(weatherDic[i][2])))), (48+32*i, 60+int(
                rate*(maxT-int(weatherDic[i+1][2])))), tft.WHITE)
        # 当日气温
        display_text(tft, (8+32*i, 42),
                     weatherDic[i][1], tft.YELLOW, half_angle_16)
        display_text(tft, (8+32*i, 110),
                     weatherDic[i][2], tft.BLUE, half_angle_16)


if __name__ == "__main__":
    update_weather()
    display_4d(tft)
