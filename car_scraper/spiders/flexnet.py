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
            r = requests.get(url, stream=True)
            with open(destfilename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            # if idx == 0:
            #     src = destfilename.split('_')[0]+'_1.jpg'
            #     copyfile(destfilename, src)
        except Exception as e:
            print(e)
            print "Error downloading file."

class BeforwardSpider(Spider):
    name = "flexnet"
    start_url = 'https://www.flexnet.co.jp/search/index.html?mkr=TO&typ=TOS196*TOS150*TOS151*TOS192*TOS149*TOS233*TOS193*TOS194*TOS195*TOS219*TOS152&upa=1993'
    # start_url = 'https://www.flexnet.co.jp/search/index_8.html?mkr=TO&typ=TOS196%2ATOS150%2ATOS151%2ATOS192%2ATOS149%2ATOS233%2ATOS193%2ATOS194%2ATOS195%2ATOS219%2ATOS152&upa=1993'

    use_selenium = False
    count = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')


    def start_requests(self):
        yield Request(self.start_url, callback= self.parse)
    def parse(self, response):
        car_urls = response.xpath('//div[@class ="zaiko_box"]')
        for car_url in car_urls:
            price_tag = car_url.xpath('.//div[@class="hiddenbox pcnone bottom10"]/dl/dd/span/text()').extract_first()
            if price_tag and price_tag != 'SOLDOUT':
                url = car_url.xpath('.//dt[@class="bottom5"]//a/@href').extract_first()
                yield Request(response.urljoin(url), callback=self.final_parse)
                # yield Request('https://www.flexnet.co.jp/detail/524805006.html', callback=self.final_parse)

        next_page_url = response.xpath('//a[@rel="next"]/@href').extract_first()
        if next_page_url:
            yield Request(response.urljoin(next_page_url), callback=self.parse)

    def final_parse(self, response):
        item = CarScraperItem()
        title= ' '.join(response.xpath('//div[@class="bknd_ttl"]/h1//text()').extract())
        # title = title.replace('車両情報', '')
        translator = Translator()
        translated_title = translator.translate(title, src='ja', dest='en')
        translated_title = re.sub('[^A-Za-z0-9 ]+', '', translated_title.text)
        yen_price = response.xpath('//span[@class="__items__price"]/text()').extract_first()
        if not yen_price:
            item['price'] = "ASK"
        else:
            yen_price = float(yen_price)*10000
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

        key_datas = response.xpath('//table[@class="usdtable bottom20"]//tr/th/text()').extract()
        val_datas = []
        tds = response.xpath('//table[@class="usdtable bottom20"]//tr/td')
        for td in tds:
            td_texts = td.xpath('.//text()').extract()
            if td_texts:
                val_text = ''.join(td_texts)
                if val_text == '-':
                    val_text = ''
                val_datas.append(val_text)
            else:
                val_datas.append('')

        for i, key in enumerate(key_datas):
            if '車体色' in key:
                item['color'] = translator.translate(val_datas[i].replace('Ⅱ',''), src='ja', dest='en').text
            elif 'ドア数' in key:
                doors = re.findall(r'\d+', val_datas[i])
                if len(doors) > 0:
                    item['doors'] = doors[0]
            elif '走行距離' in key:
                if '不明' in val_datas[i] or val_datas[i] == '': continue
                if '万' in val_datas[i]:
                    item['mileage'] = str(int(float(val_datas[i].replace('万km', '')) *10000))
                else:
                    item['mileage'] = val_datas[i].replace('km', '')

                dist_str = item['mileage']
                i = 1
                while True:
                    count = len(dist_str)
                    if count > (i*3 + (i-1)):
                        dist_str = dist_str[:count-i*3 + i-1] + ',' + dist_str[count-i*3 + i-1:]
                    else:
                        break
                    i+=1
                item['mileage'] =dist_str + "km"
            elif 'エンジン種別' in key:
                item['disel_petrol'] = translator.translate(val_datas[i], src='ja', dest='en').text
            elif '駆動方式' in key:
                item['drive'] = val_datas[i].replace('WD', 'wheel drive')
            elif 'ハンドル' in key:
                steering = translator.translate(val_datas[i], src='ja', dest='en').text
                if len(steering) > 1:
                    item['steering'] = steering.upper() + steering[1:]
                else:
                    item['steering'] = ''
            elif '排気量' in key:
                item['engine_size'] = val_datas[i]
            elif '年式' in key:
                year = re.findall('(\d+)', val_datas[i])[0]
                item['car_name'] = year +' ' + translated_title.encode('utf-8', 'ignore')
            elif '定員' in key:
                doors = re.findall(r'\d+', val_datas[i])
                if len(doors) > 0:
                    item['seats'] = doors[0]
            elif '型式' in key:
                item['model_code'] = val_datas[i]

            elif 'シフト' in key:
                if 'AT' in val_datas[i]:
                    item['transmiss'] = 'Automatic'
                elif 'MT' in val_datas[i]:
                    item['transmiss'] = 'Manual'

        item['ref_no'] = 'FX'+response.url.split('/')[-1].replace('.html', '')
        item['carCheck'] = 4

        imageUrls = response.xpath('//div[@class="p-detail__slider swiper-wrapper"]//img/@src').extract()
        pdf_path = "../scraperimages/" + item['ref_no']+ "/"
        if not os.path.exists(pdf_path):
            os.makedirs(pdf_path)
        for idx, img in enumerate(imageUrls):
            if idx != (len(imageUrls) -1):
                filename = item['ref_no'] + "_" + str(idx+1) + ".jpg"
            else:
                filename = item['ref_no'] + "_" + "0.jpg"
            download( img, pdf_path+filename, pdf_path, idx)

        yield item






