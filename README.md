
##getepg.py
    通过央视cntv接口，获取央视，和上星卫视的节目单，写入同目录下epg.xml文件，文件格式符合xmltv标准
    接口返回的json转换成dict后类似如下
    {'cctv1': {'isLive': '九九第1集', 'liveSt': 1535264130, 'channelName': 'CCTV-1 综合', 'program': [{'t': '生活提示2018-187', 'st': 1535215320, 'et': 1535215680, 'showTime': '00:42', 'eventType': '', 'eventId': '', 'duration': 360}

    Args:
        fhandle,文件处理对象，用于后续调用，直接写入xml文件
        channelID,电视台列表，list格式，可以批量一次性获取多个节目单

    Return:
        None,直接写入xml文件

##logo文件夹
    央视和上星卫视台标资源，名称同央视json接口对电视台的命名

##iptv.m3u
    电信iptv湖北版，组播频道列表，转换成udpxy格式
