# # -*- coding: utf-8 -*-
# from scrapy import Spider, Request, FormRequest
# from urlparse import urlparse
# import sys
# import re, os, requests, urllib
# from scrapy.utils.response import open_in_browser
# from collections import OrderedDict
# import time
# from shutil import copyfile
# import json, re, csv
# from car_scraper.items import CarScraperItem
# from PIL import Image
# from resizeimage import resizeimage
# import bigcommerce
#
# def download(url, destfilename, temppath):
#     filename = temppath+'tmp'
#     if not os.path.exists(destfilename):
#         print "Downloading from {} to {}...".format(url, filename)
#         try:
#             r = requests.get(url, stream=True)
#             with open(filename, 'wb') as f:
#                 for chunk in r.iter_content(chunk_size=1024):
#                     if chunk:
#                         f.write(chunk)
#                         f.flush()
#
#             with Image.open(filename) as image:
#                 cover = resizeimage.resize_cover(image, [640, 430])
#                 cover.save(destfilename, image.format)
#             os.remove(filename)
#         except Exception as e:
#             print(e)
#             print "Error downloading file."
#
# class BeforwardSpider(Spider):
#     name = "bigsite"
#     start_url = 'https://mypage.beforward.jp'
#     domain1 = 'https://mypage.beforward.jp'
#
#     use_selenium = False
#     count = 0
#     pageIndex = 1
#     reload(sys)
#     sys.setdefaultencoding('utf-8')
#
#    # //////// angel headers and cookies////////////
#     headers = {
#                 'Cache-Control': 'max-age=0',
#                 'upgrade-insecure-requests': '1',
#                 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
#                 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#                 'accept-encoding': 'gzip, deflate, br',
#                 'accept-language': 'en-US,en;q=0.9',
#                 'upgrade-insecure-requests': '1',
#                 'referer': 'https://www.tradecarview.com/my/favoritelist.aspx?list=1&sort=0&ps=25&&pn=0'
#             }
#     # cookies = {'_angellist' :'a71a277ab05568d2fe069eb936c75c05'}
#
#     def start_requests(self):
#         param = {
#             'X-Auth-Token': '1dq72h082squa7xbofqaa9670ocl6nc',
#             # 'X-Auth-Client': '7rmk66juft0eyv51mid8fpbryynk649',
#             'X-Auth-Client': 'hha9essrms482l887ofxgvsqg1xwkag',
#             'Accept':'application/json',
#             'Content-Type':'application/json',
#             # 'NAME': 'FleetReadOnly',
#             # 'API PATH': 'https://api.bigcommerce.com/stores/vpslo31z/v3/'
#         }
#
#         headers = {
#                 'X-Auth-Token': '57iuada9o6cczp6kya32l8dmaxkitys',
#             # 'X-Auth-Client': '7rmk66juft0eyv51mid8fpbryynk649',
#             'X-Auth-Client': '461f3io4er8z6hxfmg32l30vds19yhb',
#             'Accept':'application/json',
#             'Content-Type':'application/json',
#             }
#
#         url = 'https://api.bigcommerce.com/stores/vpslo31z/v3/catalog/products'
#         # url = 'https://api.bigcommerce.com/stores/vpslo31z/v3/6crr1i4olf/products'
#         yield Request(url, callback= self.parse, headers=param)
#         # tpnho4er3u
# # https://api.bigcommerce.com/stores/6crr1i4olf/v3/
#
# # Client ID
# # 461f3io4er8z6hxfmg32l30vds19yhb
# #
# # Client Secret
# # hr2kf5g2odz577oobp2r5scl0wnpmtb
# #
# # Access Token
# # 57iuada9o6cczp6kya32l8dmaxkitys
#
#
#     def parse(self, response):
#         json_data = json.loads(response.body)
#         api = bigcommerce.api.BigcommerceApi(client_id='461f3io4er8z6hxfmg32l30vds19yhb', store_hash='6crr1i4olf', access_token='57iuada9o6cczp6kya32l8dmaxkitys')
#         data = api.Products.all()
#         for product in json_data['data']:
#             # try:
#             url = 'https://api.bigcommerce.com/stores/6crr1i4olf/v3/catalog/products'
#             formdata = {}
#             headers = {
#                 'X-Auth-Token': '57iuada9o6cczp6kya32l8dmaxkitys',
#             'X-Auth-Client': 'hr2kf5g2odz577oobp2r5scl0wnpmtb',
#             # 'X-Auth-Client': '461f3io4er8z6hxfmg32l30vds19yhb',
#             'Accept':'application/json',
#             'Content-Type':'application/json',
#             }
#             # for key in product:
#             #     if not product[key]:
#             #         formdata[key] = ''
#             #     else:
#             #         formdata[key] = str(product[key])
#             product['categories'] = [23]
#             product['is_visible'] = True
#             # yield Request(url, callback=self.parse_urls,formdata=formdata, headers=headers, method='POST',)
#             r = requests.post(url, data=product, headers=headers)
#             # print r
#             #     api = bigcommerce.api.BigcommerceApi(client_id='461f3io4er8z6hxfmg32l30vds19yhb', store_hash='6crr1i4olf', access_token='57iuada9o6cczp6kya32l8dmaxkitys')
#             api.Products.create(name=product['name'], type=product['type'], price=product['price'], categories=[23], availability= product['availability'], weight=product['weight'], is_visible=product['is_visible'])
#             #     product['categories']=[23]
#             #     data = {}
#             #     api.Products.create(resource=data, data=product)
#             #     print data
#             # except Exception as e:
#             #     print e
#             #     continue
#
#         # token = response.xpath('//input[@name="_token"]/@value').extract_first()
#         # redirect_url = response.xpath('//input[@name="redirect_url"]/@value').extract_first()
#         # username = 'mjpapp@pappbrothersautomotive.com'
#         # password = '41194119mjpMJP!'
#         # formdata = {
#         #     'data[ClientLogin][login_email]': username,
#         #     'data[ClientLogin][password]': password,
#         #     'redirect_url': '/bookmark',
#         #     '_token': token
#         # }
#         # yield FormRequest(self.start_url, callback=self.parse_urls, formdata=formdata, dont_filter=True)
#
#     def parse_urls(self, response):
#         urls = response.xpath('//*[@class="vehicle"]/div[1]/a')
#         for url_tag in urls:
#             url = url_tag.xpath('./@href').extract_first()
#             yield Request(url+'&tp_country_id=90', callback=self.final_parse, dont_filter=True, headers=self.headers)
#
#         next_page_url = response.xpath('//*[@class="pagination"]/ul/li/a')
#         if next_page_url:
#             nav_txt = next_page_url[len(next_page_url) - 1].xpath('./text()').extract_first()
#             if nav_txt == 'Next':
#                 url = next_page_url[len(next_page_url) - 1].xpath('./@href').extract_first()
#                 yield Request(self.domain1 + url, callback=self.parse_urls)
#
#     def final_parse(self, response):
#         item = CarScraperItem()
#         item['car_name'] = response.xpath('//*[contains(@class, "car-info-area cf")]/h1/text()').extract_first()
#
#         # price = response.xpath('//*[@class="px18 bold green"]/span/text()').extract_first()
#         location_tags = response.xpath('//tr[@class="fn-destination-price-row"]')
#         price = None
#         for tag in location_tags:
#             location = tag.xpath('./th/text()').extract_first().strip()
#             if 'NEW YORK' in location:
#                 price = tag.xpath('.//span[@class="fn-total-price-display"]/text()').extract_first()
#                 break
#
#         if price:
#             int_price = int(price.strip().replace('$', '').replace(',', ''))
#             # priceNum = int((int_price + 1700) * 1.5)
#             priceNum = int(int_price + 2000)
#             price_str = str(priceNum)
#             i = 1
#             while True:
#                 count = len(price_str)
#                 if count > i*3:
#                     price_str = price_str[:count-i*3 + i-1] + ',' + price_str[count-i*3 + i-1:]
#                 else:
#                     break
#                 i+=1
#             price = '$' + price_str
#         else:
#             price = "ASK"
#         item['price'] = price
#
#         imageUrls = response.xpath('//*[@id="gallery"]/li/a/@href').extract()
#
#         attrs = response.xpath('//table[@class="specification"]//tr')
#         for attr in attrs:
#             keys = attr.xpath('./th')
#             vals = attr.xpath('./td/text()').extract()
#             for i, key_tag in enumerate(keys):
#                 key = key_tag.xpath('./text()').extract_first()
#                 if not key:
#                     continue
#                 if len(vals)- 1 < i:
#                     break
#                 if 'Ref No' == key:
#                     item['ref_no'] = vals[i]
#                 elif 'Location' in key:
#                     item['location'] = vals[i]
#                 elif 'Chassis' in key:
#                     item['chassis'] = vals[i]
#                 elif 'Model Code' in key:
#                     item['model_code'] = vals[i]
#                 elif 'Version/Class' in key:
#                     item['version'] = vals[i]
#                 elif 'Mileage' in key:
#                     item['mileage'] = vals[i]
#                 elif 'Engine Size' in key:
#                     item['engine_size'] = vals[i]
#                 elif 'Engine Code' in key:
#                     item['engine_code'] = vals[i]
#                 elif 'Drive' in key:
#                     item['drive'] = vals[i]
#                     if vals[i] == ' - ' or vals[i] == '':
#                         item['drive'] = "2 Wheel Drive"
#                 elif 'Ext. Color' in key:
#                     item['color'] = vals[i]
#                 elif 'Steering' in key:
#                     item['steering'] = vals[i]
#                 elif 'Transmiss' in key:
#                     item['transmiss'] = vals[i]
#                 elif 'Fuel' in key:
#                     item['disel_petrol'] = vals[i]
#                 elif 'Seats' in key:
#                     item['seats'] = vals[i]
#                 elif 'Doors' in key:
#                     item['doors'] = vals[i]
#                 elif 'Dimension' in key:
#                     item['dimension'] = vals[i].strip()
#
#
#         pdf_path = "../scraperimages/" + item['ref_no']+ "/"
#         if not os.path.exists(pdf_path):
#             os.makedirs(pdf_path)
#         for idx, img in enumerate(imageUrls):
#             filename = item['ref_no'] + "_" + str(idx) + ".jpg"
#             if "https:" in img:
#                 download(img, pdf_path+filename, pdf_path)
#             else:
#                 download("https:" + img, pdf_path+filename, pdf_path)
#
#         yield item
