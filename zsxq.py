
'''
功能：抓取知识星球专栏内容列表
1.设置UA
2.获取json
3.写入文件
4.循环执行
'''
import requests
import json
import urllib
import csv
import time
import random


#头信息。网站只提供扫码登陆的方式，没有账号密码。header信息里Authorization，直接可以保持登陆状态。
# 令一个标志是直接在浏览器里访问内页网址的话，浏览器的报错是“{"succeeded":false,"code":401,"info":"","resp_data":{}}”，这个很像原来node.js的数据中心没有登陆的报错，而数据中心的模拟登陆也是通过在header中添加Authorization来实现的。
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Referer': 'https://wx.zsxq.com/',
    'Authorization': '4809F8D1-6C0F-55F4-7B3A-264484185121_25CFEA757B3EB5AF'
    # Cookie里的 zsxq_access_token 就是 Authorization
}

#打开并写入csv文件

f = open('/Users/shuita/Downloads/zsxq.csv', 'w+')
# 打开文件后，会对原有内容进行清空，并对该文件有读写权限。
writer = csv.writer(f)
writer.writerow(['created_time','ask_name','ask_content','comment'])

#定义爬取信息的函数主体

def get_zsxq(url):
    res = requests.get(url,headers = headers)
    json_data = json.loads(res.text)  
    datas = json_data['resp_data']['topics']
    print(res.status_code)
    # if(res.status_code>200):
    for data in datas:
        if 'talk' in data.keys(): # 判断json中是否包含 talk 这个键，没有这个就等于没有内容
            ask_name = data['talk']['owner']['name']
            ask_content = data['talk']['text']
            if 'images' in data['talk'].keys():
                images=data['talk']['images'][0]['thumbnail']['url']
                # print(data['talk']['images'][0]['thumbnail']['url'])，如果有图片就单独讲图片写入表格       
            else:
                images=''
        else:
            ask_name = ''
            ask_content = ''
        if 'show_comments' in data.keys():
            comment = data['show_comments']
        else:
            comment = ''
        created_time = data['create_time']
        writer.writerow([created_time,ask_name,ask_content,comment,images,])

    # 截止到前面的代码，已经可以实现一个页面的爬取。下面的代码内容主要任务是实现“如何自动实现多页面爬取”
    # 多页面的爬取是通过Network中Query String Parameters来实现的：这里提供两个参数，观察之后发现count是固定值，而end_time和网址最后的时间是一样的。
    # 只不过在网页中用到了 urlencode的转化
    # 网页构造的核心逻辑是“上一组最后一个数据的创建时间刚好是下一组数据访问网址中的一个参数”，以此来构造循环抓取的网址

    end_time = datas[19]['create_time']
    # 取最后一个talk的时间
    url_encode = urllib.parse.quote(end_time) # urlencode，将网址中的文本转化
    next_url = 'https://api.zsxq.com/v2/groups/88855122548212/topics?scope=all&count=20&end_time='+url_encode # 通过观察构造下一组数据的网址
    s=random.randrange(0, 101,1)
    # 设置定时函数1-100秒内随机执行，模拟用户真实情况，要不然知识星球会认为是抓取
    time.sleep(s)
    get_zsxq(next_url) # 这里比较巧，直接在函数内部再次调用函数，从而实现不断的自循环
if __name__ == '__main__':
    url="https://api.zsxq.com/v2/groups/88855122548212/topics?count=20"
    get_zsxq(url)
