# coding=utf-8
import os
import httpx
import re
import time

# CONFIG PART =====================================
uid = os.environ["UID"]
SendKey = os.environ["SENDKEY"]
minSpeed = float(os.environ["MINSPEED"])
minMileage = int(os.environ["MINMILEAGE"])

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    'Host': 'hdu.sunnysport.org.cn',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'http://hdu.sunnysport.org.cn',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://hdu.sunnysport.org.cn/login/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

session = httpx.Client()
r = session.get('http://hdu.sunnysport.org.cn/login/',headers=header)
# 下面是为了应对set-cookie无效所搞的无奈之举 所以实际上也没有必要使用Client了
header['Cookie'] = re.match('(sessionid=.*?);',r.headers.get('set-cookie')).group(1)
print("complete")
vrf = re.search('name="vrf" value="(.*?)">', r.content.decode()).group(1)

loginData = {
    'username': uid,
    'vrf': vrf,
    'password': uid
    # important if you not change the init password as your uid
    # if you do that please add Secret to your own
}

r = session.post('http://hdu.sunnysport.org.cn/login/',headers=header,data=loginData,allow_redirects=False)
header['Cookie'] = re.match('(sessionid=.*?);',r.headers.get('set-cookie')).group(1)

# 拿数据
totalRecord = session.get('http://hdu.sunnysport.org.cn/runner/data/speed.json',headers=header).json()
print(totalRecord)

# 因为懒得写正则 所以目前的有效次数和有效里程都是从总的数据里直接算的
totalMileage = 0
validMileage = 0
totalTimes = 0
validTimes = 0

todayRecord = {}
if time.strftime("%Y-%m-%d", time.localtime()) in totalRecord[len(totalRecord)-1]['runnerTime']:
    todayRecord = totalRecord[len(totalRecord)-1]
    for dayRecord in totalRecord:
        totalMileage += dayRecord['runnerMileage']
        totalTimes += 1
        if dayRecord['runnerSpeed'] > minSpeed and dayRecord['runnerMileage'] > minMileage:
            validMileage += dayRecord['runnerMileage']
            validTimes += 1

if todayRecord:
    desp = '今日跑步距离：{}\n\n今日跑步速度：{}\n\n---\n\n'.format(todayRecord['runnerMileage'],round(todayRecord['runnerSpeed'],2))
    desp += '总里程：{}\n\n总次数：{}\n\n---\n\n'.format(totalMileage,totalTimes)
    desp += '有效里程：{}\n\n有效次数：{}\n\n---\n\n'.format(totalMileage,totalTimes)
    print(desp)
    # 推数据
    msg2send = {
        'title': '阳光长跑记录已更新',
        'desp': desp
    }
    httpx.post('https://sctapi.ftqq.com/{}.send'.format(SendKey),data=msg2send)
    
