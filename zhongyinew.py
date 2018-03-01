# -*- coding:utf-8 -*-
import requests, json, re, base64, zlib
import pyaes.aes
from lxml import etree
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def StartWork():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3346.9 Safari/537.36'}
    url = 'https://www.zk120.com/ji/group/?nav=ahz'
    response = requests.get(url, headers=headers).text
    html = etree.HTML(response)
    # 获取每个分类的url
    result = html.xpath('//div[@class="container"]/section[3]/ul/li/a/@href')
    for i in result:
        types_url = 'https://www.zk120.com' + str(i)
        get_url(types_url)


def get_url(types_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3346.9 Safari/537.36'}
    response = requests.get(types_url, headers=headers).text
    html = etree.HTML(response)
    # 根据每个分类的url匹配出其分类下各个书籍的url
    result = html.xpath('//p[@class="group_btns"]/a/@href')
    try:
        for i in result:
            text_url = 'https://www.zk120.com' + str(i)
            get_content(text_url)
    except:
        pass


def get_content(text_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3346.9 Safari/537.36'}
    # 将书籍内容链接里的read替换为content
    url = re.sub(r'read', 'content', text_url)
    response = requests.get(url, headers=headers).text
    # 将已编码的 JSON 字符串解码为 Python 对象
    html = json.loads(response)
    # 匹配出书名
    book_name = html['title']
    # 匹配出加密过的书籍内容
    book_content = html['data']
    # 解密
    decode = 4 - len(book_content) % 4
    if decode:
        book_content += b'=' * decode
    content = base64.decodestring(book_content)
    aes = pyaes.AESModeOfOperationCFB(key="61581af471b166682a37efe6", iv="c8f203fca312aaab", segment_size=16)
    aes_text = aes.decrypt(content)
    text_zip = json.loads(zlib.decompress(aes_text))
    text = text_zip.get("text").encode("utf-8", "ignore")
    save(book_name, text)


def save(book_name, text):
    # 打开文件，以匹配出的书名为文件名，追加写入
    with open(book_name + '.txt', 'w+')as f:
        f.write(text)
        print 'success'
        # 关闭文件
        f.close()


if __name__ == '__main__':
    StartWork()
