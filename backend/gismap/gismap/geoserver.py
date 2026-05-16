# -*- coding: utf-8 -*-

# Django 核心组件
from django.http import HttpResponse       # 用于返回纯文本/HTML 响应
from django.shortcuts import render        # 用于渲染模板文件并返回
from django.views.decorators.csrf import csrf_exempt
import requests

# HTTP 方法校验装饰器（限制视图只接受指定类型的请求）
from django.views.decorators.http import (
    require_http_methods,   # 自定义允许的 HTTP 方法列表
    require_GET,            # 只允许 GET 请求
)


# 处理 GET 搜索请求：http://.../?q=关键词
def get(request):
    request.encoding = "utf-8"
    if 'q' in request.GET and request.GET['q']:
      message = '你搜索的内容为：' + request.GET['q']
    else:
      message = '你没有搜索任何内容'
    return HttpResponse(message)


# 处理 POST 表单提交：接收表单数据并返回渲染结果
@require_http_methods(['POST'])
def posthtml(request):
    ctx = {}
    if request.POST:
      ctx['rlt'] = request.POST['q']
    return render(request, 'post.html', ctx)


# 渲染 GET 表单页面
@require_GET
def gethtml(request):
    return render(request, 'get.html')

# 获取wmts服务
def wmts(request):
    url='http://localhost:8084/geoserver/wms?SERVICE=WMS&VERSION=1.1.0&'+\
        'REQUEST=GetMap&FORMAT=image%2Fpng&TRANSPARENT=true&tiled=true&'+\
        'LAYERS='+request.GET['LAYERS']+'&exceptions=application%2Fvnd.ogc.se_inimage&singleTile=true&SRS=EPSG%3A4326&STYLES=&WIDTH='+\
        request.GET['WIDTH']+'&HEIGHT='+request.GET['HEIGHT']+'&BBOX='+request.GET['BBOX']
    print(url)
    image_data=requests.get(url=url,stream=True)
    return HttpResponse(image_data.content,content_type='image/png')


# 获取要素服务
def getfeature(request):
    url='http://localhost:8084/geoserver/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&FORMAT=image%2Fpng&'+\
        'TRANSPARENT=true&QUERY_LAYERS='+request.GET['QUERY_LAYERS']+'&LAYERS='+request.GET['LAYERS']+\
        '&exceptions=application%2Fvnd.ogc.se_inimage&INFO_FORMAT=application/json&FEATURE_COUNT=50&X=50&Y=50'+\
        '&SRS=EPSG%3A4326&STYLES=&WIDTH=101&HEIGHT=101&BBOX='+request.GET['BBOX']
    json_data=requests.get(url=url)
    if json_data.status_code != 200:
        return HttpResponse(json_data.content, content_type='text/plain', status=json_data.status_code)
    return HttpResponse(json_data.content, content_type='application/json')


# WFS 代理：前端通过 Django 转发到 GeoServer，避免 CORS 问题
@require_http_methods(['POST'])
@csrf_exempt
def wfs_proxy(request):
    url = 'http://localhost:8084/geoserver/wfs'
    response = requests.post(url=url, data=request.body, headers={'Content-Type': 'text/xml'})
    return HttpResponse(response.content, content_type='text/xml')


# 提交 gml到geoserver
def postgml(request):
    ctx ={}
    if request.POST:
        head = {"Content-Type": "text/xml; charset=UTF-8", "Connection": "close"}
        r = requests.post('http://localhost:8084/geoserver/wfs', data=request.POST['gml'], headers=head)
        ctx['rlt'] = r.text
    return render(request, "postgml.html", ctx)

# 渲染geoserver页面
def geoserverget(request):
    return render(request, 'GeoserverOL.HTML')

# 提交 gml到geoserver
def geoserverpost(request):
    if request.POST:
        head = {"Content-Type": "text/xml; charset=UTF-8", "Connection": "close"}
        r = requests.post('http://localhost:8080/geoserver/wfs', data=request.POST['gml'], headers=head)
    return HttpResponse(r.text)