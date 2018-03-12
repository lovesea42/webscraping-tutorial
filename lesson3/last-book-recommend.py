import csv
import random
from urllib import parse

import re
import requests
from bs4 import BeautifulSoup as BS

# 每页的图书数量
DOUBAN_BOOK_PAGE_SIZE = 20
# 至少的评价分数
DOUBAN_BOOK_STAR = 8.0
# 至少的评价数量
DOUBAN_BOOK_COMMENT = 10
# 错误次数,超过次数
ERROR_COUNT = 10
#代理
proxie = {
        'http' : 'http://122.193.14.102:80'
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
      def __init__(self,type):
          
          self.url = 'https://book.douban.com/tag/' + parse.quote(type) + '?type=R&start='
          self.data = []
          self.error_count = 0

      def _get_main_html(self,url):

          r = requests.get(url, headers=DOUBAN_BOOK_COMMON_HEADER,proxies = proxie,verify=False,timeout = 20)
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

              detail = self._parser_detail(url)

              if detail == None:
                  continue

              dic1 = {
                  'comment' : comment,
                  'rating_nums' : rating_nums,
                  'name' : name,
                  'url' : url,
                  'tags' : ','.join(detail['tags'])
              }
              print(rating_nums)
              print(name)
              print(comment)
              self.data.append(dic1)

      #解析详细的页面
      def _parser_detail(self,url):
          r = requests.get(url, headers=DOUBAN_BOOK_COMMON_HEADER)
          if r.status_code is not 200:
             self.error_count += 1
             return None

          content = r.text
          soup = BS(content, 'lxml')
          divs = soup.find_all(id='db-tags-section')

          tags = []
          for div in divs:
              a = div.find_all('a',{'class' : ' tag'})
              for dt in a:
                  tags.append(dt.get_text())


          return {
              "tags" : tags
          }


      def _output_to_csv(self,path):
          try:
              with open(path, 'w',newline ='') as csv_file:
                  writer = csv.writer(csv_file, dialect='excel')

                  # 先写入columns_name
                  writer.writerow(["name", "comment", "rating_nums","tags"])

                  self.data = sorted(self.data, key=lambda x: float(x['comment']) * x['rating_nums'],reverse=True)

                  for dt in self.data:
                     writer.writerow([dt["name"],dt["comment"],dt["rating_nums"],dt["tags"]])

          except Exception as e:
              print("Write an CSV file to path: %s, Case: %s" % (path,e))

      def get_data_by_page(self,page):
          for page in range(0,page):
              #判断是否超过最大错误次数
              if self.error_count > ERROR_COUNT:
                  break

              url = self.url + str(page * DOUBAN_BOOK_PAGE_SIZE)
              html = self._get_main_html(url)

          self._output_to_csv("/test1.csv")


if __name__ == '__main__':
    douban = DoubanBookRecommend('编程')
    douban.get_data_by_page(1)

