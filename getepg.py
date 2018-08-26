#-*- coding: utf-8 -*-                                                                                                                                  
import re
import requests
from datetime import datetime

def getChannel(fhandle, channelID):
    '''
    通过央视cntv接口，获取央视，和上星卫视的节目单，写入同目录下epg.xml文件，文件格式符合xmltv标准
    接口返回的json转换成dict后类似如下
    {'cctv1': {'isLive': '九九第1集', 'liveSt': 1535264130, 'channelName': 'CCTV-1 综合', 'program': [{'t': '生活提示2018-187', 'st': 1535215320, 'et': 1535215680, 'showTime': '00:42', 'eventType': '', 'eventId': '', 'duration': 360}

    Args:
        fhandle,文件处理对象，用于后续调用，直接写入xml文件
        channelID,电视台列表，list格式，可以批量一次性获取多个节目单

    Return:
        None,直接写入xml文件
    '''

    #change channelID list to str cids
    cids = ''
    for x in channelID:
        cids = cids + x + ','

    epgdate = datetime.now().strftime('%Y%m%d')
    session = requests.Session()
    api = "http://api.cntv.cn/epg/epginfo?c=%s&d=%s" % (cids, epgdate)
    epgdata = session.get(api).json()

    for n in range(len(channelID)):
        program = epgdata[channelID[n]]['program']

        #write channel id info
        fhandle.write('    <channel id="%s">\n' % channelID[n])
        fhandle.write('        <display-name lang="cn">%s</display-name>\n' % epgdata[channelID[n]]['channelName'])
        fhandle.write('    </channel>\n')
        
        #write programe
        for detail in program:
            st = datetime.fromtimestamp(detail['st']).strftime('%Y%m%d%H%M')+'00'
            et = datetime.fromtimestamp(detail['et']).strftime('%Y%m%d%H%M')+'00'

            fhandle.write('    <programme start="%s" stop="%s" channel="%s">\n' % (st, et, channelID[n]))
            fhandle.write('        <title lang="cn">%s</title>\n' % detail['t'])
            fhandle.write('    </programme>\n')

cctv_channel = ['cctv1','cctv2','cctv3','cctv4','cctv5','cctv5plus','cctv6','cctv7','cctv8','cctvjilu','cctv10','cctv11','cctv12']
sat_channel = ['hubei','hunan','zhejiang','jiangsu','dongfang','btv1','guangdong','shenzhen','heilongjiang','tianjin','shandong','anhui','liaoning']

with open('epg.xml','at') as fhandle:
    fhandle.write('<?xml version="1.0" encoding="utf-8" ?>\n')
    fhandle.write('<tv>\n')
    getChannel(fhandle, cctv_channel)
    getChannel(fhandle, sat_channel)
    fhandle.write('</tv>')
