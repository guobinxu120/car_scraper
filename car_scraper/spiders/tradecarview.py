# -*- coding: utf-8 -*-
from scrapy import Spider, Request, FormRequest
from urlparse import urlparse
import sys
import re, os, requests, urllib
from collections import OrderedDict
import time
import json, re, csv
from car_scraper.items import CarScraperItem
from PIL import Image
from resizeimage import resizeimage

def download(url, destfilename, idx):
    filename = destfilename
    time.sleep(2)
    if not os.path.exists(destfilename):
        if idx == 0:
            filename = destfilename+'tmp'

        print "Downloading from {} to {}...".format(url, filename)
        try:
            r = requests.get(url, stream=True)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            if idx == 0:
                with Image.open(filename) as image:
                    cover = resizeimage.resize_cover(image, [700, 410])
                    cover.save(destfilename, image.format)
        except:
            print "Error downloading file."




class TradecarviewSpider(Spider):
    name = "tradecarview"
    start_url = 'https://www.tradecarview.com/my/favoritelist.aspx?list=100+username+%3d+mpapp'
    domain1 = 'https://www.tradecarview.com'

    use_selenium = False
    count = 0
    pageIndex = 1
    reload(sys)
    sys.setdefaultencoding('utf-8')

   # //////// angel headers and cookies////////////
    headers = {
                'Cache-Control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'upgrade-insecure-requests': '1',
                'referer': 'https://www.tradecarview.com/my/favoritelist.aspx?list=1&sort=0&ps=25&&pn=0'
            }

    def start_requests(self):
        yield Request(self.start_url, callback= self.parse,dont_filter=True)
    def parse(self, response):

        username = 'mjpapp@pappbrothersautomotive.com'
        password = '41194119mjpMJP!'

        return FormRequest.from_response(response=response,
                                            formdata={'ctl00$cph$lb1$TextBox_Account': username, 'ctl00$cph$lb1$TextBox_Password': password},
                                            clickdata={'id': 'ctl00_cph_lb1_Button_Login'},
                                            callback=self.parse_urls, dont_filter=True)

    def parse_urls(self, response):
        urls = response.xpath('//table[@id="table_list"]/tbody/tr/td[3]/a')
        # urls = response.xpath('//table[@id="table_list"]/tbody/tr/td[3]/a')
        for url_tag in urls:
            carname = url_tag.xpath('./text()').extract_first()
            url = url_tag.xpath('./@href').extract_first()
            yield Request(url, callback=self.final_parse, dont_filter=True, meta={'carname':carname}, headers=self.headers)
            # break
        next_page_url = response.xpath('//*[@id="ctl00_cph_sc_pg1_HLN"]/@href').extract_first()
        if next_page_url:
            yield Request(self.domain1 + next_page_url, callback=self.parse_urls)

    def final_parse(self, response):
        item = CarScraperItem()
        item['car_name'] = response.xpath('//*[@class="used-detail-ttl"]/text()').extract_first().encode('utf-8').strip()

        price = response.xpath('//*[@id="Car_Price"]/text()').extract_first()
        if price:
            int_price = int(price.replace('US$', '').replace(',', ''))
            priceNum = int(int_price + 3000)
            price_str = str(priceNum)
            i = 1
            while True:
                count = len(price_str)
                if count > i*3:
                    price_str = price_str[:count-i*3 + i-1] + ',' + price_str[count-i*3 + i-1:]
                else:
                    break
                i+=1
            price = '$' + price_str
        else:
            price = "ASK"
        item['price'] = price

        imageUrls = response.xpath('//*[@class="image-gallery-thumb-list used-pic-thumb-list"]/li/a/@data-img').extract()


        chassis = response.xpath('//*[@class="car-info-table"]/tbody/tr[1]/td/div/text()').extract_first()
        if chassis:
            chassis = chassis.replace('***', '')
        else:
            return
        # item['ref_no'] = "TCV" + chassis
        item['chassis'] = chassis


        attrs = response.xpath('//*[@class="car-info-table"]/tbody/tr')
        for i, attr in enumerate(attrs):
            key = attr.xpath('./th/text()').extract_first()
            val = attr.xpath('./td/text()').extract_first()
            if 'Model Code' in key:
                if val != '-':
                    item['model_code'] = val.encode('utf-8', 'ignore')
                else:
                    item['model_code'] = ''
            elif 'Mileage' in key:
                item['mileage'] = val
            elif 'Engine Capacity' in key:
                item['engine_size'] = val
            elif 'Drive Type' in key:
                if val == '':
                    val = "2 Wheel Drive"
                item['drive'] = val
            elif 'Steering' in key:
                item['steering'] = val
            elif 'Transmission' in key:
                item['transmiss'] = val
            elif 'Exterior Color' in key:
                item['color'] = val
            elif 'Fuel' in key:
                item['disel_petrol'] = val
            elif 'Seats' in key:
                item['seats'] = val
            elif 'Door' in key:
                item['doors'] = val
            elif 'Dimension' in key:
                item['dimension'] = val
            elif 'ID' in key:
                item['ref_no'] = "TCV" + val

        pdf_path = "../scraperimages/" + item['ref_no']+ "/"
        if not os.path.exists(pdf_path):
            os.makedirs(pdf_path)

        # for idx, img in enumerate(imageUrls):
        #     filename = item['ref_no'] + "_" + str(idx) + ".jpg"
        #     download(img, pdf_path+filename, idx)

        id = response.url.replace('/?sp=17', '').split('/')[-1]
        formdata = {
            'iiids': id,
            'icn': '840',
            'ipt': '32823',
            'iir': '1',
            'iip': '1',
            'ifr': '1',
            'ier': '1'
        }
        # yield item
        yield FormRequest('https://www.tradecarview.com/include/include_totalprice.aspx?lang=en', callback=self.getDeliveryPrice, formdata=formdata, meta={'item':item})

    def getDeliveryPrice(self, response):
        price_data = json.loads(response.body)
        item = response.meta['item']
        try:
            price = int(price_data['odata'][0]['tp'])
            if price > 0:
                priceNum = price + 2000
                price_str = str(priceNum)
                i = 1
                while True:
                    count = len(price_str)
                    if count > i*3:
                        price_str = price_str[:count-i*3 + i-1] + ',' + price_str[count-i*3 + i-1:]
                    else:
                        break
                    i+=1
                item['price'] = '$' + price_str
        except:
            pass

        yield item









