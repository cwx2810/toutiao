import json
from urllib.parse import urlencode
from hashlib import md5
import re

import os
import pymongo
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
from config import *

#声明数据库对象，传入地址、名称
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

#获取索引页
def get_page_index(offset, keyword):
    #从保存日志的offset中拿到get请求参数，保存成字典形式
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 1
    }
    #构造完整url，用urllib库提供的方法把字典转换成请求参数
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    #请求url，赋值给response
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None

#解析索引页，通过索引页的json拿到详情页的url
def parse_page_index(html):
    #把json转换成对象
    data = json.loads(html)
    #如果json中有数据，就遍历之，取出详情页的url字段
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

#通过上一步的url解析详情页，拿到详情页信息
def get_page_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错', url)
        return None

#拿到详情页信息后，解析详情页
def parse_page_detail(html, url):
    #用BS提取html的title
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    #用正则表达式提取图片链接，这里用原来的.*?不能匹配换行，而S*可以匹配到换行
    images_pattern = re.compile('gallery: ([\s\S]*),[\s\S]*siblingList:', re.S)
    #匹配
    result = re.search(images_pattern, html)
    #判断匹配是否成功
    if result:
        #提取json中的sub_images字段
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            #sub_images本身又是一个键值对的形式的列表，那我们也用列表保存它
            images = [item.get('url') for item in sub_images]
            for image in images:download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }

#定义保存到数据库的方法
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到mongoDB成功！', result)
        return True
    return False

#请求下载页
def download_image(url):
    print('正在下载', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_images(response.content)
        return None
    except RequestException:
        print('请求下载页出错', url)
        return None

#解析下载页，保存图片
def save_images(content):
    #定义文件名：项目路径/防止重名的名字.jpg
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    #如果此文件不存在，就可以保存了
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main():
    html = get_page_index(0, '杨颖')
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result:save_to_mongo(result)

if __name__ == '__main__':
    main()