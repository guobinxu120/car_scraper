# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CarScraperItem(scrapy.Item):
    car_name = scrapy.Field()
    price = scrapy.Field()
    ref_no = scrapy.Field()
    chassis = scrapy.Field()
    model_code = scrapy.Field()
    engine_size = scrapy.Field()
    drive = scrapy.Field()
    transmiss = scrapy.Field()
    location = scrapy.Field()
    version = scrapy.Field()
    mileage = scrapy.Field()
    engine_code = scrapy.Field()
    steering = scrapy.Field()
    color = scrapy.Field()
    disel_petrol = scrapy.Field()
    seats = scrapy.Field()
    doors = scrapy.Field()
    dimension = scrapy.Field()
    carCheck = scrapy.Field()