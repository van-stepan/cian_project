# -*- coding: utf-8 -*-

import os
import lxml.html as html
from lxml import etree
import urllib2
import re
import datetime
import time
import glob
import codecs

base_url = "http://mosopen.ru/regions"
page = urllib2.urlopen(base_url)


doc = html.document_fromstring(page.read())
query = etree.XPath("//table[@class = 'regions_list']//a")
regions = query(doc)


lines = []
regions_data = []


file = "C:\\MSK_ADDRESS_BOOK.TXT"
if not os.path.exists(file):
    fid = open(file, 'w')
    fid.close()
    
fid = open(file, 'a')


for region in regions:
    regions_data.append( [region.get("href"), region.text_content()] )

for i in range(len(regions_data)):
    
    item = regions_data[i]
    
    region_link = item[0]
    region_name = item[1]
    
    streets_page = urllib2.urlopen(region_link + "/streets")
    streets_list_doc = html.document_fromstring(streets_page.read())
    streets_query = etree.XPath("//div[@class = 'double_part']//a")
    streets = streets_query(streets_list_doc)
    
    if streets == []:
        streets_query = etree.XPath("//p[@class = 'compact']/following-sibling::ul[1]//a")
        streets = streets_query(streets_list_doc)
        
    streets_data = []
    
    for street in streets:
        streets_data.append( [street.get("href"), street.text_content()] )
        
    for street_item in streets_data:
        
        street_link = street_item[0]
        street_name = street_item[1]
        
        houses_page = urllib2.urlopen(street_link)
        houses_list_doc = html.document_fromstring(houses_page.read())
        houses_query = etree.XPath("//p//a[contains(@href, 'address')]")
        houses = houses_query(houses_list_doc)
        
        for house in houses:
        
            line = region_name + " | " + street_name + " | " + house.text_content()
            fid.write(line + "\n")
            print line
            
fid.close()
        
