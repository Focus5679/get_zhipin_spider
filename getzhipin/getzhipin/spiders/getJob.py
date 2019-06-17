# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import re
import chardet


class GetjobSpider(scrapy.Spider):
    name = 'getJob'
    baseurl = 'https://www.zhipin.com/'

    def start_requests(self):  #用于发起初始爬取请求
        urls = ['https://www.zhipin.com/']
        #发起爬取请求，依次爬取urls列表中的url
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse)  #设置处理函数

    def parse(self, response):  #处理第一个爬取页面
        soup = BeautifulSoup(
            response.body,
            'html.parser')  #使用BeautifulSoup库中html.parser解析请求到的页面
        div_tech = soup.find('div', attrs={'class': 'menu-sub'})  #获取需要爬取的技术方向
        div_city = soup.find('div', attrs={'class': 'slider-city'})  #获取需要爬取的城市
            
        cnt = 0  # 测试：计数为mx时结束产生新的爬取请求，防止封IP
        mx = 3  # 测试：最大爬取页数

        #遍历技术限定条件与城市限定条件下的每一页页面
        for a_tech in div_tech.find_all('a'):
            for a_city in div_city.find_all('a'):
                for page in range(1, 11):
                    try:
                        cnt += 1
                        tech_word = a_tech.attrs['href'][11:]  #技术限定条件
                        city_word = a_city.attrs['href'][:-1]  #城市限定条件
                        page_word = '?page=' + str(page)  #页码限定条件
                        techDirection = a_tech.string
                        yield scrapy.Request(
                            self.baseurl + city_word + tech_word +
                            page_word,  #利用限定条件拼接url
                            meta={'techDirection':techDirection},
                            callback=self.parse_joblist)

                    except:#当发生异常时，可以跳过发生异常的页码，继续进行数据爬取
                        continue
                    #测试：达到限定条件时停止发起新的请求
                    finally:
                        if cnt == mx:
                            break
                if cnt == mx:
                    break

            if cnt == mx:
                break

    def parse_joblist(self, response):  #获取加入限定条件后的职位列表
        #Debug代码：输出获取的网址url到文件
        # filename = 'test.txt'
        # with open(filename, 'a') as f:
        #     f.write(response.url + '\n')

        #炖一锅汤，获取需要爬取得职位列表
        soup = BeautifulSoup(response.body, 'html.parser')

        div_poslist = soup.find('div', attrs={'class': 'job-list'})
        techDirection = response.meta['techDirection']

        cnt = 0  # 测试：计数为mx时结束产生新的爬取请求，防止封IP
        mx = 5  # 测试：最大爬取岗位数

        #遍历职位列表
        for li in div_poslist.find_all('li'):
            try:
                cnt += 1
                
                info = {}#建立存储数据的字典
                #依次从页面中解析出需要的数据项
                nexthref = li.find('a')['href']
                jobname = li.find('div', attrs={'class': 'job-title'}).string
                salary = li.find('span', attrs={'class': 'red'}).string  #
                primaryinfo = str(li.find('p')).strip('<p/>').split(
                    '<em class="vline"></em>')
                companyname = li.find('div', attrs={
                    'class': 'company-text'
                }).find('a').string
                companyinfo = str(li.find_all('p')[1]).strip('<p/>').split(
                    '<em class="vline"></em>')
                
                #将解析出的各项数据存储在info字典中
                info['jobName'] = jobname
                info['salary'] = salary
                info['city'] = primaryinfo[0]
                info['workYear'] = primaryinfo[1]
                info['education'] = primaryinfo[2]
                info['companyShortName'] = companyname
                info['techDirection'] = techDirection
                info['financeStage'] = companyinfo[1]
                info['companySize'] = companyinfo[2]
                #发起多级爬取请求，进入每个职位的页面进行爬取
                yield scrapy.Request(self.baseurl + nexthref,
                                     meta={'info': info},
                                     callback=self.parse_job)

            except:
                continue
            #测试：达到限定条件时停止发起新的请求
            finally:
                if cnt == mx:
                    break

    def parse_job(self, response):
        #Debug代码：输出获取的网址url到文件
        # filename = 'test.txt'
        # with open(filename, 'a') as f:
        #     f.write(response.url + '\n')

        #先获取上页未补全得info信息，然后炖汤
        info = response.meta['info']
        soup = BeautifulSoup(response.body, 'html.parser')

        try:
            #解析出需要的数据项
            jobdetail = soup.find('div', attrs={'class': 'text'}).text.strip('\n ')
            posttime = soup.find('p', attrs={'class': 'gray'}).string
            #companydetail = soup.find_all('div', attrs={'class': 'text'})[1].text.strip('\n ')

            #将解析出的各项数据存储在info字典中
            info['jobDetail'] = jobdetail
            info['postTime'] = posttime
            info['success'] = 1
            #info['companyDetail'] = companydetail
        except:
            info['success'] = 0
        finally:
            #Debug代码：输出获取的信息到文件
            # filename = 'test.txt'
            # with open(filename, 'a') as f:
            #     f.write(str(info) + '\n')
            yield info
