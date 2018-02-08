import csv
from urllib import parse

import re
import requests
from bs4 import BeautifulSoup as BS

# 页的数量
DOUBAN_BOOK_PAGE_SIZE = 20
# 至少的评价分数
DOUBAN_BOOK_STAR = 8.0
# 至少的评价数量
DOUBAN_BOOK_COMMENT = 10

class DoubanBookRecommend:

      #初始化爬虫url
      def __init__(self,type):

          self.url = 'https://book.douban.com/tag/' + parse.quote(type) + '?type=R&start='
          self.data = []

      def _get_main_html(self,url):
          headers = {
              'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
          r = requests.get(url, headers=headers)
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
              comment = div.find_all(class_='pl')

              if len(comment) == 0:
                  continue

              comment = int(re.sub("\D", "", rating[0].get_text()))

              if comment < DOUBAN_BOOK_COMMENT:
                  continue

              dic1 = {
                  'comment' : comment,
                  'rating_nums' : rating_nums,
                  'name' : name
              }
              print(rating_nums)
              print(name)
              print(comment)
              self.data.append(dic1)


      def _output_to_csv(self,path):
          try:
              with open(path, 'w',newline ='') as csv_file:
                  writer = csv.writer(csv_file, dialect='excel')

                  # 先写入columns_name
                  writer.writerow(["name", "comment", "rating_nums"])

                  self.data = sorted(self.data, key=lambda x: float(x['comment']) * x['rating_nums'],reverse=True)

                  for dt in self.data:
                     writer.writerow([dt["name"],dt["comment"],dt["rating_nums"]])

          except Exception as e:
              print("Write an CSV file to path: %s, Case: %s" % (path,e))

      def get_data_by_page(self,page):
          for page in range(0,page):
              url = self.url + str(page * DOUBAN_BOOK_PAGE_SIZE)
              html = self._get_main_html(url)

          self._output_to_csv("D:/test1.csv")


if __name__ == '__main__':
    douban = DoubanBookRecommend('编程')
    douban.get_data_by_page(100)

