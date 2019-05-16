#-*- coding: utf-8 -*-                                                                                                                                  
import re
import requests
from lxml import html
from datetime import datetime

cctv_channel = ['cctv1','cctv2','cctv3','cctv4','cctv5','cctv5plus','cctv6','cctv7','cctv8','cctvjilu','cctv10','cctv11','cctv12']
cctv_channel_tvsou = ['cctv-1','cctv-2','cctv-3','cctv-4','cctv-5','cctv5+','cctv-6','cctv-7','cctv-8','cctv-9','cctv-10','cctv-11','cctv-12']
cctv_channel_tvmining = {'CCTV1HD':['cctv1','CCTV-1 HD'], 'CCTV2HD':['cctv2','CCTV-2 HD'], 'CCTV3HD':['cctv3','CCTV-3 HD'], \
        'CCTV4HD':['cctv4','CCTV-4 HD'], 'CCTV5HD':['cctv5','CCTV-5 HD'], 'CCTV5AHD':['cctv5plus','CCTV-5+ HD'], \
        'CCTV6HD':['cctv6','CCTV-6 HD'], 'CCTV7HD':['cctv7','CCTV-7 HD'], 'CCTV8HD':['cctv8','CCTV-8 HD'], \
        'CCTV9HD':['cctv9','CCTV-9 HD'], 'CCTV10HD':['cctv10','CCTV-10 HD'], 'CCTV11HD':['cctv11','CCTV-11 HD'],\
        'CCTV12HD':['cctv12','CCTV-12 HD']}

sat_channel_tvmining = {'HuBeiHD':['hubei','湖北卫视 HD'],'HuNanHD':['hunan','湖南卫视 HD'],'ZheJiangHD':['zhejiang','浙江卫视 HD'], \
        'JiangSuHD':['jiangsu','江苏卫视 HD'],'SHDongFangHD':['dongfang','东方卫视 HD'],'BTV1':['btv1','北京卫视 HD'], \
        'GuangDongHD':['guangdong','广东卫视 HD'],'ShengZhengHD':['shenzhen','深圳卫视 HD'], 'HeiLongJiangHD':['heilongjiang','黑龙江卫视 HD'], \
        'TianJingHD':['tianjin','天津卫视 HD'],'ShanDongHD':['shandong','山东卫视 HD'],'AnHuiHD':['anhui','安徽卫视 HD'], \
        'LiaoNingHD':['liaoning','辽宁卫视 HD']}

sat_channel = ['hubei','hunan','zhejiang','jiangsu','dongfang','btv1','guangdong','shenzhen','heilongjiang','tianjin','shandong','anhui','liaoning']
sat_channel_tvsou = ['hubei','hunan','zhejiang','jiangsu','dongfang','btv1','guangdong','shenzhen','heilongjiang','tianjin','shandong','anhui','liaoning']

def getChannelCNTV(fhandle, channelID):
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

def getChannelTVsou(fhandle, channelID):
    '''
    获取TVSOU的节目单和节目信息，先获取所有台的ID，再通过ID获取每个台每天节目单

    '''
    #获取tvsou每个台的地址
    session = requests.Session()
    base_url = 'https://www.tvsou.com'
    api_url = 'https://www.tvsou.com/epg/%s/' % channelID
    headers = {'Host':'www.tvsou.com','User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'}
    #获取所有电视台的url的xpath
    channels_rule = '/html/body/div[3]/div[3]/div[3]/div[1]/div[1]/ul/li/a/@href'
    channelname_rule = '/html/body/div[3]/div[2]/span[2]/text()'
    epgname_rule = '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div[2]/ol/li/@data-name'
    epgtime_rule = '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div[2]/ol/li/@data-mainstars'
    epgcontenturl_rule = '/html/body/div[3]/div[3]/div[3]/div[2]/div[2]/div[2]/ol/li/@data-url'
    epgcontentdesc_url = '/html/body/div[3]/div[1]/div[1]/div/div/div/pre/text()'

    #获取所有电视台的URL，方便抓取
    channels_html= session.get(api_url,headers=headers).text
    tree = html.fromstring(channels_html)
    channels_url = tree.xpath(channels_rule)

    #按照获取的url抓取电视台节目单
    for channel in channels_url:
        c_html = session.get(base_url + channel,headers=headers).text
        tree = html.fromstring(c_html)
        #epgname可以直接使用，epgtime和epgcontenturl需要转换
        channelid = channel.split('?')[0].split('/')[-1]
        #channelname = tree.xpath(channelname_rule)[0].strip().split(' ')[0].split('台-')[1]
        channelname = re.match(r'.*?-(.*) 节目单',tree.xpath(channelname_rule)[0].strip()).group(1)
        epgname = tree.xpath(epgname_rule)
        epgtime = tree.xpath(epgtime_rule)
        epgcontenturl = tree.xpath(epgcontenturl_rule)

        #转换epg节目单的content为节目真实url
        epgcontenturl = [base_url+i.strip().replace('show','story') for i in epgcontenturl]
        epgstarttime = [datetime.now().strftime('%Y%m%d')+j[0].replace(':','').strip() for j in [i.split('-') for i in epgtime]]
        epgstoptime = [datetime.now().strftime('%Y%m%d')+j[1].replace(':','').strip() for j in [i.split('-') for i in epgtime]]

        #write channel id info
        fhandle.write('    <channel id="%s">\n' % channelid)
        fhandle.write('        <display-name lang="cn">%s</display-name>\n' % channelname)
        fhandle.write('    </channel>\n')

        #write programe
        for n in range(len(epgname)):

            #获取节目的描述desc，需要额外在抓取网页的描述信息
            #desc_html = session.get(epgcontenturl[n][0:-1],headers=headers).text
            #tree = html.fromstring(desc_html)
            #desc_content = tree.xpath(epgcontentdesc_url[0])
            #print(desc_content)


            fhandle.write('    <programme start="%s" stop="%s" channel="%s">\n' % (epgstarttime[n], epgstoptime[n], channelid))
            fhandle.write('        <title lang="cn">%s</title>\n' % epgname[n].strip())
            #fhandle.write('        <desc lang="cn">%s</desc>\n' % epgname[n].strip())
            fhandle.write('    </programme>\n')

def getChannelTVmining(fhandle,channelID):
    '''
    获取tvmining的电子节目单，给出的xml格式，直接转换成json后组合成标准节目单即可
    '''

    epgdate = datetime.now().strftime('%Y-%m-%d')
    session = requests.Session()

    #节目单信息正则表达式获取
    re_title = re.compile(r'<title>(.*?)</title>')
    re_start = re.compile(r'<start_time>(.*?)</start_time>')
    re_end = re.compile(r'<end_time>(.*?)</end_time>')

    for n in channelID.keys():
        api_url = "http://stream.suntv.tvmining.com/approve/epginfo?channel=%s&date=%s" % (n,epgdate)
        epgdata = session.get(api_url).text

        title = re_title.findall(epgdata)
        start_time = re_start.findall(epgdata)
        end_time = re_end.findall(epgdata)
        start_time_epg = [datetime.fromtimestamp(int(st)).strftime('%Y%m%d%H%M')+'00' for st in start_time]
        end_time_epg = [datetime.fromtimestamp(int(et)).strftime('%Y%m%d%H%M')+'00' for et in end_time]

        fhandle.write('    <channel id="%s">\n' % channelID[n][0])
        fhandle.write('        <display-name lang="cn">%s</display-name>\n' % channelID[n][1])
        fhandle.write('    </channel>\n')

        for i in range(len(title)):

            fhandle.write('    <programme start="%s" stop="%s" channel="%s">\n' % (start_time_epg[i], end_time_epg[i], channelID[n][0]))
            fhandle.write('        <title lang="cn">%s</title>\n' % title[i])
            fhandle.write('    </programme>\n')


#with open('/var/www/html/iptv/epg.xml','at') as fhandle:
with open('epg.xml','at') as fhandle:
    fhandle.write('<?xml version="1.0" encoding="utf-8" ?>\n')
    fhandle.write('<tv>\n')
#    getChannelTVsou(fhandle,cctv_channel_tvsou)
#    getChannelTVsou(fhandle, 'weishi')
#    getChannelCNTV(fhandle, cctv_channel)
#    getChannelCNTV(fhandle, sat_channel)
    getChannelTVmining(fhandle,cctv_channel_tvmining)
    getChannelTVmining(fhandle,sat_channel_tvmining)
    fhandle.write('</tv>')
