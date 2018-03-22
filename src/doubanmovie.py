import csv
import random
import re
import threading
from urllib import parse

import requests
import sys
from bs4 import BeautifulSoup as BS

from pymongo import MongoClient

# 页的数量
DOUBAN_BOOK_PAGE_SIZE = 20
# 至少的评价分数
DOUBAN_BOOK_STAR = 8.0
# 至少的评价数量
DOUBAN_BOOK_COMMENT = 10

proxie = {
        'http' : 'http://223.244.99.107:61234'
    }

DOUBAN_BOOK_COMMON_HEADER = {
              'Host':"book.douban.com",
              "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
              "Accept-Encoding": "gzip, deflate, br",
              "Accept-Language": "zh-CN,zh;q=0.9",
               "Connection": "keep-alive",
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}

class DoubanBookRecommend:

      #初始化爬虫url
      def __init__(self,type,host,port):

          print ('初始化爬虫开始...')
          self.url = 'https://book.douban.com/tag/' + parse.quote(type) + '?type=R&start='
          self.data = []
          self.conn = MongoClient(host, port)
          self.db = self.conn.book

      def _get_main_html(self,url):

          print('爬虫开始%s...' % (url))
          r = requests.get(url, headers=DOUBAN_BOOK_COMMON_HEADER, proxies=proxie, verify=False, timeout=20)
          content = r.text
          #print(content)

          soup = BS(content, 'lxml')
          divs = soup.find_all(class_ = 'info')

          #print(divs)

          for div in divs:
              #获取书名
              name = div.a.get_text().replace("\n","")
              name = " ".join(name.split())
              #判断评价数和评价分
              rating = div.find_all(class_ = 'rating_nums')

              #没有评分
              if len(rating) == 0:
                  continue

              rating_nums = float(rating[0].get_text())
              if rating_nums < DOUBAN_BOOK_STAR :
                  continue

              #判断评价人数
              comment = div.find(class_='pl')

              if len(comment) == 0:
                  continue

              comment = int(re.sub("\D", "", rating[0].get_text()))

              if comment < DOUBAN_BOOK_COMMENT:
                  continue

              # 获取url
              url = div.find('a').get('href')

              if len(url) == 0:
                  continue

              author = ''
              price = 0.0
              date = ''
              publisher = ''

              # 获取pub信息
              pub = div.find(class_='pub')
              if pub:
                  pub = pub.get_text()

                  pub = ''.join(pub.split())
                  pub = pub.split('/')
                  size = len(pub)
                  author = pub[0]
                  price = float(re.findall(r"\d+\.?\d*", pub[size - 1])[0])
                  date = pub[size - 2]
                  publisher = pub[size - 3]

              detail = self._parser_detail(url)

              dic1 = {
                  'comment' : comment,
                  'rating_nums' : rating_nums,
                  'name' : name,
                  'url' : url,
                  'tags' : ','.join(detail['tags']),
                  'isbn' : detail['isbn'],
                  'author' : author,
                  'price' : price,
                   'date' : date,
                  'publisher':publisher,
                  '_id' : detail['isbn'],
                  'img' : detail['img']
              }
              print(dic1)
              self.data.append(dic1)

              self._output_to_csv("book.csv")
              self._output_to_mongodb(dic1)

      #解析详细的页面
      def _parser_detail(self,url):
          r = requests.get(url, headers=DOUBAN_BOOK_COMMON_HEADER)
          content = r.text
          soup = BS(content, 'lxml')
          divs = soup.find_all(id='db-tags-section')


          tags = []
          for div in divs:
              a = div.find_all('a',{'class' : ' tag'})
              for dt in a:
                  tags.append(dt.get_text())

          isbn = -1
          info = soup.find(id='info')
          if info:
              isbn = info.find('span',text='ISBN:')
              if isbn:
                  isbnp = isbn.parent.text
                  isbn_num = re.search(r'ISBN: (\d+)',isbnp,re.M|re.I)
                  if isbn_num:
                      isbn = isbn_num.group(1)

          nbg = soup.find(class_='nbg')
          img = ''
          if nbg:
              img = nbg['href']

          return {
              "tags" : tags,
              "isbn" : str(isbn),
              "img" : img
          }

      def add_book_data(self, data):
          try:
             self.db.dangdang.insert(data)
          except Exception as e:
              print("error to insert data to mongodb %s" %e)


      def _output_to_mongodb(self,data):
           self.add_book_data(data)


      def _output_to_csv(self,path):
          try:
              with open(path, 'w',newline ='') as csv_file:
                  writer = csv.writer(csv_file, dialect='excel')

                  # 先写入columns_name
                  writer.writerow(["name","isbn", "comment", "rating_nums","tags"])

                  self.data = sorted(self.data, key=lambda x: float(x['comment']) * x['rating_nums'],reverse=True)

                  for dt in self.data:
                     writer.writerow([dt["name"],dt["isbn"],dt["comment"],dt["rating_nums"],dt["tags"]])

          except Exception as e:
              print("Write an CSV file to path: %s, Case: %s" % (path,e))

      def get_data_by_page(self,page):

          self.db.dangdang.remove()

          #thread = []
          for page in range(0,page):
              url = self.url + str(page * DOUBAN_BOOK_PAGE_SIZE)
              self._get_main_html(url)
              # t = threading.Thread(target=self._get_main_html,
              #                      args=(url,))
          #     thread.append(t)
          #
          # for i in range(0, page):
          #     thread[i].start()
          #
          # for i in range(0, page):
          #     thread[i].join()

if __name__ == '__main__':
    douban = DoubanBookRecommend('编程','localhost',27017)
    page = int(sys.argv[1])
    print('本次爬虫页数：%d' % (page))
    douban.get_data_by_page(page)

