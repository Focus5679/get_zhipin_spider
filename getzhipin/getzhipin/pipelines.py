# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class GetzhipinPipeline(object):
    def process_item(self, item, spider):
        return item


class GetzhipinJobInfoPipeline(object):
    def open_spider(self, spider):
        self.conn = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    password='********',
                                    db='zhipinjob',
                                    charset='utf8')
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()
        self.cursor.close()

    def process_item(self, info, spider):
        if info['success'] == 1:
            try:
                #将爬取到的数据插入数据库
                self.cursor.execute(
                    '''insert into joblist
                    (
                        jobName, salary, city,
                        workYear, education,
                        companyShortName, techDirection,
                        financeStage, companySize,
                        jobDetail, postTime
                    )
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                    [
                        info['jobName'], info['salary'], info['city'],
                        info['workYear'], info['education'],
                        info['companyShortName'], info['techDirection'],
                        info['financeStage'], info['companySize'],
                        info['jobDetail'], info['postTime']
                    ])
                self.conn.commit()
            except:
                pass
        return info
