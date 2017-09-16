import json
from urllib.parse import urlencode

import re
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests

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
def parse_page_detail(html):
    #用BS提取html的title
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    #用正则表达式提取图片链接
    images_pattern = re.compile('gallery: {(.*?)},', re.S)
    #匹配
    result = re.search(images_pattern, html)
    #判断匹配是否成功
    if result:
        print(result.group(1))

def main():
    html = get_page_index(0, '杨颖')
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            parse_page_detail(html)


if __name__ == '__main__':
    main()