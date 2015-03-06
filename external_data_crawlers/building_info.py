# -*- coding: utf-8 -*-

import sys 
import os
import lxml
import lxml.html
from lxml import etree
import codecs
from string import maketrans
import urllib2
import re

print help(lxml)

# ******* EXTRACT DISTRICT NAMES **********
# 
# filename = "C:\\cian_pages_sell\\Misc\\Msk Districts\\wiki_page.txt"
# txt = codecs.open(filename, 'r', 'cp1251').read()
# doc = lxml.html.document_fromstring(unicode(txt))
# 
# distrs = ""
# elems = doc.xpath("//a[@class = 'CategoryTreeLabel  CategoryTreeLabelNs14 CategoryTreeLabelCategory']")
# for item in elems:
#     distrs = distrs + item.text_content() + "\n"
#     
# res = codecs.open("C:\\cian_pages_sell\\Misc\\Msk Districts\\LIST.txt", 'w')
# res.write(distrs)
# res.close()
# 
# ******* END **********


# ******* EXTRACT DISTRICT NAMES and LINKS **********
# 
# filename = "C:\\cian_pages_sell\\Misc\\Msk Districts\\mosopen_regions_page.txt"
# txt = codecs.open(filename, 'r', 'cp1251').read()
# doc = lxml.html.document_fromstring(unicode(txt))
#  
# distrs = ""
# elems = doc.xpath("//a[contains(@href, 'http://mosopen.ru/region/')]")
# print len(elems)
# for item in elems:
#     distrs = distrs + item.xpath('@href')[0] + '|' + item.text_content() + "\n"
#      
# res = codecs.open("C:\\cian_pages_sell\\Misc\\Msk Districts\\REGION_LIST.txt", 'w')
# res.write(distrs)
# res.close()
# 
# ******* END **********





# ******* TRANSLATE DISTRICT NAMES **********
# 
# filename = "C:\\cian_pages_sell\\Misc\\Msk Districts\\REGION_LIST.txt"
# districts = open(filename).readlines()
# for i in range(len(districts)):
#     districts[i] = districts[i].split('|')


def getDistricts():
    
    fid = open("C:\cian_pages_sell\Misc\Msk Districts\MOSCOW_STREET_LIST.txt")


def getDistrictStreets(district_url):
    
    streets = []
    url = district_url + "/streets"
    print url
    txt = urllib2.urlopen(url).read()
    doc = lxml.html.document_fromstring(unicode(txt))

    elems = doc.xpath("//a[contains(@href, 'http://mosopen.ru/street/')]")
    for item in elems:
        street = item.text_content()
        streets.append(street)

    return streets


# streets = []
# res_fid = open("C:\\cian_pages_sell\\Misc\\Msk Districts\\REGION_STREET_LIST.txt", 'w')
# 
# for district in districts:
#     
#     url = "http" + district[0].split("http")[1]
#     distr_streets = getDistrictStreets(url) 
#     for street in distr_streets:
#         data = district[1].strip() + "; " + street + "\n"
#         print "DATA: " + data
#         streets.append(data)
# 
# res_fid.writelines(streets)
# res_fid.close()
# # 
# ******* END **********
'''
# ****** CLEAN MOSCOW STREETS ******
street_types = [u"улица", u"переулок", u"проезд",
                u"площадь", u"проспект", u"шоссе",
                u"тупик", u"мост", u"набережная",
                u"посёлок", u"линия", u"бульвар", u"аллея",
                u"парк", u"квартал", u"просека",
                u"микрорайон", u"деревня", "пойма"]

file = "C:\cian_pages_sell\Misc\Msk Districts\MOSCOW_STREET_LIST.txt"
new_file = "C:\cian_pages_sell\Misc\Msk Districts\MOSCOW_STREET_LIST_FILTERED.txt"
new_streets = []
fid = open(file)
streets = fid.readlines()
fid.close()


none_type_cnt = 0
for i in range(len(streets)):

    streets[i] = streets[i].split("(")[0].strip()
    street_type = None
    street_name = streets[i]
    
    for type in street_types:
        if streets[i].lower().find(type) != -1:
             street_type = type
             break
         
    if street_type == None:
        continue
    else:
        street_name = streets[i].replace(street_type, '').replace(';','').replace(',','').strip()
    print street_name + " : " + str(street_type)
#     new_streets.append(street_name + " : " + street_type + "\n")    
        

# fid = open(new_file, 'w')
# fid.writelines(new_streets)
# fid.close()'''