#!/usr/bin/python
# encoding: utf-8

import sys
import os
from datetime import date, datetime, timedelta
from workflow import Workflow3

def query_weather(wf, city):
    import requests

    api_key = os.getenv('api_key')
    if api_key == '':
        wf.add_item('APIKey 未设置','请设置api_key的环境变量')
        return

    # 商业版
    base_url = 'https://api.heweather.net/s6/weather/{weather_type}'

    # 查询实时天气
    url = base_url.format(weather_type='now')
    r = requests.get(url, params = {'location': city, 'key':api_key})
    if r.status_code != requests.codes.ok:
        wf.add_item('请求异常','请求错误：'+ r.status_code)
        return
    weather_info = r.json()
    if weather_info['HeWeather6'][0]['status'] != 'ok':
        if weather_info['HeWeather6'][0]['status'] == 'unknown location':
            wf.add_item('请输入正确的城市')
            return
        wf.add_item('请求异常','请求错误：'+ weather_info['HeWeather6']['status'])
        # log.error(weather_info)
        return
    
    # 城市
    weather_city = weather_info['HeWeather6'][0]['basic']['location']
    # 更新时间
    update_time = weather_info['HeWeather6'][0]['update']['loc']
    # 温度
    weather_tmp = weather_info['HeWeather6'][0]['now']['tmp']
    # 天气对应图标
    weather_code = weather_info['HeWeather6'][0]['now']['cond_code'] 
    # 天气描述
    weather_txt = weather_info['HeWeather6'][0]['now']['cond_txt']  
    # 天气图标
    weather_icon = weather_info['HeWeather6'][0]['now']['cond_code']  
    
    title = u'【{}】当前温度{}°C，{}'.format(weather_city, weather_tmp, weather_txt)
    sub_title = u'  当前天气（更新时间：{}）'.format(update_time)
    icon_path = './res/icon-heweather/{}.png'.format(weather_icon)
    wf.add_item(title,sub_title,icon=icon_path)    
    
    # 查询未来天气
    url = base_url.format(weather_type='forecast')
    r = requests.get(url, params = {'location': city, 'key':api_key})
    if r.status_code != requests.codes.ok:
        wf.add_item('请求异常','请求错误：'+ r.status_code)
        return
    weather_info = r.json()
    if weather_info['HeWeather6'][0]['status'] != 'ok':
        wf.add_item('请求异常','请求错误：'+ weather_info['HeWeather6']['status'])
        # log.error(weather_info)
        return
    # 城市
    weather_city = weather_info['HeWeather6'][0]['basic']['location']
    date = ['今天', '明天', '后天']
    for index in range(3):
        weather_future = weather_info['HeWeather6'][0]['daily_forecast'][index]
        # 最高温度和最低温度
        tmp_max = weather_future['tmp_max']
        tmp_min = weather_future['tmp_min']
        # 白天和夜晚
        cond_txt_d = weather_future['cond_txt_d']
        cond_txt_n = weather_future['cond_txt_n']
        title = u'【{}】{}白天{}，夜间{}，温度{}°C~{}°C'.format(weather_city, wf.decode(date[index]), cond_txt_d,cond_txt_n,tmp_min,tmp_max)
        weater_date, weater_week = get_date(index)
        sub_title = '   {}   {}   {}'.format(date[index], weater_date, weater_week)
         # 天气图标
        weather_icon = weather_future['cond_code_d']  
        icon_path = './res/icon-heweather/{}.png'.format(weather_icon)
        wf.add_item(title,sub_title,icon=icon_path)

def get_date(offset=0):
    """
     获取某一天的日期信息.
     args: timedelta 往后查询的天数，默认为0是查询今天
     return: {日期}, {星期}
    """
    week = {
        'Mon' : '星期一' , 
        'Tue' : '星期二' ,
        'Wed' : '星期三' ,
        'Thu' : '星期四' ,
        'Fri' : '星期五' ,
        'Sat' : '星期六' ,
        'Sun' : '星期日'
    }
    day = date.today()
    if offset!= 0:
        day = datetime.now() + timedelta(days=offset)
    return day.strftime('%m月%d日'), week[day.strftime('%a')]


def main(wf):
    query = "auto_ip"
    if len(wf.args) and wf.args[0] != "":
        query = wf.args[0]
    query_weather(wf, query)
    wf.send_feedback()
    
if __name__ == '__main__':
    wf = Workflow3(libraries=['./lib'])
    # log = wf.logger
    sys.exit(wf.run(main))