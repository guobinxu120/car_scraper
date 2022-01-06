# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
from urlparse import urlparse
import sys
import re, os, requests, urllib
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import time
from shutil import copyfile
import json, re, csv
from car_scraper.items import CarScraperItem
from PIL import Image
from resizeimage import resizeimage
# from googletrans import Translator
# from currency_converter import CurrencyConverter

def download(url, destfilename, temppath, idx):
    filename = temppath+'tmp'
    if not os.path.exists(destfilename):
        print "Downloading from {} to {}...".format(url, filename)
        try:
            if idx == 0:
                r = requests.get(url, stream=True)
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()

                with Image.open(filename) as image:
                    cover = resizeimage.resize_cover(image, [640, 320])
                    cover.save(destfilename, image.format)
                os.remove(filename)
            else:
                r = requests.get(url, stream=True)
                with open(destfilename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()
        except Exception as e:
            print(e)
            print "Error downloading file."

class BeforwardSpider(Spider):
    name = "fujicars"
    start_url = 'http://www.fujicars.jp/search.php?view=1&body=&sort=publish2&shop=&mission=&maker=1&name=&color=&priceL=0&priceH=0&keyword=&motor=&nenshikiL=0&nenshikiH=1993&oil=&exhaustL=0&exhaustH=0'
    # domain1 = 'https://mypage.beforward.jp'

    use_selenium = False
    count = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')
    translater_words={
       'トヨタ': 'TOYOTA',
    }

    def start_requests(self):
        yield Request(self.start_url, callback= self.parse)
    def parse(self, response):
        car_urls = response.xpath('//table[@class ="carListBlockTable"]//div[@class="carThumb"]/a/@href').extract()
        for car_url in car_urls:
            yield Request(response.urljoin(car_url), callback=self.final_parse)
    # def parse_urls(self, response):
    #     urls = response.xpath('//*[@class="vehicle"]/div[1]/a')
    #     for url_tag in urls:
    #         url = url_tag.xpath('./@href').extract_first()
    #         yield Request(url+'&tp_country_id=90', callback=self.final_parse, dont_filter=True, headers=self.headers)
    #
    #     next_page_url = response.xpath('//*[@class="pagination"]/ul/li/a')
    #     if next_page_url:
    #         nav_txt = next_page_url[len(next_page_url) - 1].xpath('./text()').extract_first()
    #         if nav_txt == 'Next':
    #             url = next_page_url[len(next_page_url) - 1].xpath('./@href').extract_first()
    #             yield Request(self.domain1 + url, callback=self.parse_urls)

    def final_parse(self, response):
        item = CarScraperItem()
        title= response.xpath('//div[@class="contentBox"]/h2/span/text()').extract_first()
        title = title.replace('車両情報', '')
        translator = Translator()
        translated_title = translator.translate(title, src='ja', dest='en')



        yen_price = response.xpath('//p[@class="price"]/span/text()').extract_first().replace('円', '').replace(',', '')
        if 'SOLD OUT' in yen_price:
            item['price'] = "ASK"
        else:
            c = CurrencyConverter()
            usd_price = c.convert(yen_price, 'JPY', 'USD')
            price_str = str(int(usd_price + 3500))
            i = 1
            while True:
                count = len(price_str)
                if count > i*3:
                    price_str = price_str[:count-i*3 + i-1] + ',' + price_str[count-i*3 + i-1:]
                else:
                    break
                i+=1
            item['price'] = '$' + price_str

        key_datas = response.xpath('//table[@class="specTable"]//tr/th/text()').extract()
        val_datas = response.xpath('//table[@class="specTable"]//tr/td/text()').extract()
        for i, key in enumerate(key_datas):
            if 'カラー' in key:
                item['color'] = translator.translate(val_datas[i].replace('Ⅱ',''), src='ja', dest='en').text
            elif 'ドア枚数' in key:
                doors = re.findall(r'\d+', val_datas[i])
                if len(doors) > 0:
                    item['doors'] = doors[0]
            elif '走行' in key:
                item['mileage'] = val_datas[i]
            elif '燃料' in key:
                engeen_types = val_datas[i].split('/')
                if len(engeen_types) > 1:
                    item['disel_petrol'] = translator.translate(engeen_types[1], src='ja', dest='en').text
                    wheels= re.findall(r'\d+', engeen_types[2])
                    if len(wheels) > 0:
                        item['drive'] = wheels[0]+'wheel drive'
            elif '排気量' in key:
                item['engine_size'] = val_datas[i]
            elif '年式' in key:
                year = re.findall('\((\d+)', val_datas[i])[0]
                item['car_name'] = year +' ' + translated_title.text

        item['ref_no'] = 'FJ'+response.url.split('/')[-2]

        imageUrls = response.xpath('//div[@class="printMode"]/ul/li/img/@src').extract()
        pdf_path = "../scraperimages/" + item['ref_no']+ "/"
        if not os.path.exists(pdf_path):
            os.makedirs(pdf_path)
        for idx, img in enumerate(imageUrls):
            filename = item['ref_no'] + "_" + str(idx) + ".jpg"
            download(response.url.replace('index.html', img), pdf_path+filename, pdf_path, idx)

        yield item






