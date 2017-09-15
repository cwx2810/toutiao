import json
from urllib.parse import urlencode
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

def main():
    html = get_page_index(0, '杨颖')
    for url in parse_page_index(html):
        print(url)

if __name__ == '__main__':
    main()