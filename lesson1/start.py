from urllib import parse

import requests

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    r = requests.get('https://book.douban.com/tag/' + parse.quote('编程') + '?type=R')
    content = r.text
    print(content)

