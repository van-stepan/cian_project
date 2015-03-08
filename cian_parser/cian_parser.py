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
import logging
from support import lists

class CianParser:
    
    def __init__(self, url_pattern = ".", file_pattern = "."):
        
        self.url_pattern = url_pattern
        self.file_pattern = file_pattern
        self.page = "."
        self.ads = "."
        self.names = lists.names
        self.metro_stations = lists.metro_stations

    def savePage(self, file_suffix, page):
            
        filename = self.file_pattern + file_suffix + '.txt'
        fid = open(filename, 'w')
        page_lines = page.split('\n')
        for i in range(len(page_lines)):
            page_lines[i] = page_lines[i] + "\n"
        fid.writelines( page_lines )
        fid.close()
            
    def getPage(self, url_suffix):
            
        page = "."
        try:
            url = self.url_pattern + url_suffix
            page = urllib2.urlopen(url)
        except Exception, e:
            
            msg = "ERROR (getPage): " + repr(e)
            print msg
            logging.error(msg)
            return "."
        
        return page.read()
        
    def setPage(self, page):
        
        self.page = page
        self.setAds()
        return
    
    def setPageFromFile(self, filename, enc = 'utf8'):
        
        try:
            fid = open(filename, 'r')
            page = codecs.decode(fid.read(), enc)
            fid.close()
            self.page = page
            self.setAds()
            
        except Exception, e:
            
            msg = "ERROR (setPageFromFile): " + repr(e)
            print msg
            logging.error(msg)
    
    def setAds(self):
        
        try:
            doc = html.document_fromstring(self.page)
            find_ads_query = etree.XPath("//tr[contains(@id, 'offer_')]")
            self.ads = find_ads_query(doc)
            
        except Exception, e:
            
            msg = "ERROR (setAds): " + repr(e)
            print msg
            logging.error(msg)
        
        
    def getAds(self):
        
        return self.ads
        
    
# *********************
# GENERAL AD INFO
# *********************
    
    
    
    def getAdID(self, ad):
        
        aid = -1
        aid_search_pattern = "./@id"
        try:
            aid_objects = ad.xpath(aid_search_pattern)
            if aid_objects != []:
                aid = int(aid_objects[0].split(u"_")[1])
            else:
                aid = -1
        except Exception, e:
            
            msg = "ERROR (getAdID): " + repr(e)
            print msg
            logging.error(msg)
            aid = -1
            pass
        
        return aid
    
    
    def getAdLink(self, ad, opcode):
        
        if opcode == "SELL":
            link = u"http://www.cian.ru/sale/flat/"
        else:
            link = u"http://www.cian.ru/rent/flat/"
            
        try:
            ID = self.getAdID(ad)
            if ID != -1:
                link = link + str(ID)
                
        except Exception, e:
            
            msg = "ERROR (getAdLink): " + repr(e)
            print msg
            logging.error(msg)
            link = u"."
            pass
        
        return link
        
    
    def getRoomCount(self, ad):
        
        room_count = "."
        if self.page != ".":
            
            try:
                room_count_objects = ad.xpath(".//div[@class = 'objects_item_info_col_w']/a")
                if room_count_objects != []:
                    room_count = room_count_objects[0].text_content().strip()
                    
            except Exception, e:
                
                msg = "ERROR (getRoomCount): " + repr(e)
                print msg
                logging.error(msg)
                pass

        return room_count
    
# *********************
# PRICES
# *********************    
    
    def getPrice(self, ad, opcode):
        
        price = -1
        if self.page != u".":
            
            try:
                
                try:
                    
                    price_object = ad.xpath(u".//div[@class = 'objects_item_price']")
                    
                except Exception, e:
                    
                    msg = "ERROR (getPrice -> price_object): " + repr(e)
                    print msg
                    logging.error(msg)
                    pass
                
                try:
                    
                    price = price_object[0].text_content()
                    price = int( re.sub("[^0-9]", "", price) )
                    
                except Exception, e:
                    
                    msg = "ERROR (getPrice -> price cleansing): " + repr(e)
                    print msg
                    logging.error(msg)
                    price = -1
                    pass
                
            except Exception, e:
                
                msg = "ERROR (getPrice): " + repr(e)
                print msg
                logging.error(msg)
                price = -1
            
        return price
    
    
    def getPricePerSquareMeter(self, ad):
        
        price_sqm = -1
        if self.page != ".":
            
            try:
                
                find_price_sqm_div = etree.XPath(".//div[@style = 'color:green;']")
                price_sqm_object = find_price_sqm_div(ad)
                price_sqm = price_sqm_object[0].text_content()
                price_sqm = price_sqm.replace(u"м2", "")
                price_sqm = int( re.sub("[^0-9]", "", price_sqm) )
                
            except Exception, e:
                
                msg = "ERROR (getPricePerSquareMeter): " + repr(e)
                print msg
                logging.error(msg)
                price_sqm = -1
                pass
            
        return price_sqm


    def getCurrency(self, ad, opcode):
        
        currency = u"."
        if self.page != u".":
            
            try:
                currency = ad.xpath(".//div[@class = 'objects_item_price']")
                currency = currency[0].text_content()
                    
                if currency.find(u"$") != -1:
                    currency = u"$"
                else:
                    if currency.find(u"€") != -1:
                        currency = u"€"
                    else:
                        currency = u"руб"
                        
            except Exception, e:
                
                msg = "ERROR (getCurrency): " + repr(e)
                print msg
                logging.error(msg)
                pass
            
        return currency
    
    

# *********************
# CITY & ADDRESS
# *********************
    
    
    def getCity(self, ad):
        
        city = u"."
        if self.page != u".":
            
            try:
                city_object = ad.xpath(".//div[@class = 'objects_item_addr']")
                city = city_object[0].text_content().strip().replace("\"", "").replace("\'", "")
            except Exception, e:
                
                msg = "ERROR (getCity): " + repr(e)
                print msg
                logging.error(msg)
                pass
            
        return city
    
    
    def getRaion(self, ad):
        
        raion = u"."
        if self.page != u".":
            
            try:
                
                city_object = ad.xpath(".//div[@class = 'objects_item_addr']/a[contains(@href, 'raion') and not(contains(@href, 'city'))]")
                if city_object != []:
                    raion = city_object[0].text_content().strip().replace("\"", "").replace("\'", "")
                    
            except Exception, e:
                
                msg = "ERROR (getRaion): " + repr(e)
                print msg
                logging.error(msg)
                pass
            
        return raion
    
    
    def getRaionCity(self, ad):
        
        raion_city = u"."
        if self.page != u".":
            
            try:
                
                city_object = ad.xpath(".//div[@class = 'objects_item_addr']/a[contains(@href, 'raion') and contains(@href, 'city')]")
                if city_object != []:
                    raion_city = city_object[0].text_content().strip().replace("\"", "").replace("\'", "")
                    
            except Exception, e:
                
                msg = "ERROR (getRaionCity): " + repr(e)
                print msg
                logging.error(msg)
                pass
            
        return raion_city
    
    
    def getStreet(self, ad):
        
        street = u"."
        if self.page != u".":
            
            try:
                
                city_object = ad.xpath(".//div[@class = 'objects_item_addr']/a[contains(@href, 'street') and not(contains(@href, 'house'))]")
                if city_object != []:
                    street = city_object[0].text_content().strip().replace("\"", "").replace("\'", "")
                    
            except Exception, e:
                
                msg = "ERROR (getStreet): " + repr(e)
                print msg
                logging.error(msg)
                pass
            
        return street
    
    
    def getHouse(self, ad):
        
        house = u"."
        if self.page != u".":
            
            try:
                
                city_object = ad.xpath(".//div[@class = 'objects_item_addr']/a[contains(@href, 'street') and contains(@href, 'house')]")
                if city_object != []:
                    house = city_object[0].text_content().strip()
                    
            except Exception, e:
                
                msg = "ERROR (getHouse): " + repr(e)
                print msg
                logging.error(msg)
                pass

        return house


    
# *********************
# METRO STATION MATTERS
# *********************
    
    
    
    def getMetroStation(self, ad):
        
        metro = "."
        if self.page != ".":
            
            try:
                
                metro_object = ad.xpath(".//div[@class = 'objects_item_metro']/a")
                if metro_object != []:
                    metro = metro_object[0].text_content().strip()
                    
            except Exception, e:
                
                msg = "ERROR (getMetroStation): " + repr(e)
                print msg
                logging.error(msg)
                pass
            
        return metro
    
    
    def getMetroStationDistrict(self, ad):
        
        district = '.'
        try:
            
            metro = self.getMetroStation(ad).replace("м.", "").strip()
            district = lists.getDistrictByMetroStation(metro)
            
        except Exception, e:
            
            msg = "ERROR (getMetroStationDistrict): " + repr(e)
            print msg
            logging.error(msg)
            pass
        
        return district
    
    
    def getMinutesToMetro(self, ad):
        
        min_to_metro = -1
        if self.page != ".":
            
            try:
                
                min_to_metro_object = ad.xpath(".//div[@class = 'objects_item_metro']/span[@class = 'objects_item_metro_comment']")
                if min_to_metro_object != []:
                    
                    min_to_metro = min_to_metro_object[0].text_content().strip()
                    
                    try:
                        min_to_metro = int(re.sub("[^0-9]", "", min_to_metro))
                    except:
                        min_to_metro = -1
                        pass
                        
            except Exception, e:
                
                msg = "ERROR (getMinutesToMetro): " + repr(e)
                print msg
                logging.error(msg)
                min_to_metro = -1
                pass

        return min_to_metro
    
    
    def getByWhatToMetro(self, ad):
        
        by_what = "."
        if self.page != ".":
            
            try:
                min_to_metro_object = ad.xpath(".//div[@class = 'objects_item_metro']/span[@class = 'objects_item_metro_comment']")
                if min_to_metro_object != []:
                    if min_to_metro_object[0].text_content().strip().find("пешк") != -1:
                        by_what = "ПЕШКОМ"
                    else:
                        try:
                            min_to_metro = int(self.getMinutesToMetro(ad))
                            by_what = "АВТО"
                        except Exception, e:
                            pass
                        
            except Exception, e:
                
                msg = "ERROR (getByWhatToMetro): " + repr(e)
                print msg
                logging.error(msg)
                pass

        return by_what
    
    
    def getMinToMetroConverted(self, mins, bywhat):
        
        mins_converted = -1
        try:
            
            if mins != -1:
                
                if bywhat == 'АВТО':
                    mins_converted = int(mins) * 10
                else:
                    mins_converted = int(mins) 
            
        except Exception, e:
            
            msg = "ERROR (getMinToMetroConverted): " + repr(e)
            print msg
            logging.error(msg)
            mins_converted = -1
            pass
        
        return mins_converted
        
        
    
# *********************
# FLAT AREA FIGURES
# *********************
    
    
    
    def getAreaTotal(self, ad):
        
        area_total = -1
        if self.page != ".":
            
            try:
                
                area_objects = ad.xpath(".//table[@class = 'objects_item_props']//td")
                if area_objects != []:
                    for area_object in area_objects:
                        text = area_object.text_content().strip().replace("м2", "")
                        if text.find("Общая") != -1:
                            area_total = int(re.sub("[^0-9]", "", text))
                            break
                        
            except Exception, e:
                
                msg = "ERROR (getAreaTotal): " + repr(e)
                print msg
                logging.error(msg)
                area_total = -1
                pass

        return area_total
    
    
    def getAreaBedroom(self, ad):
        
        area_bedroom = -1
        if self.page != ".":
            
            try:
                
                area_objects = ad.xpath(".//table[@class = 'objects_item_props']//td")
                if area_objects != []:
                    for area_object in area_objects:
                        text = area_object.text_content().strip().replace("м2", "")
                        if text.find("Жилая") == -1 and text.find("Кухня") == -1 and text.find("Общая") == -1:
                            area_bedroom = int(re.sub("[^0-9]", "", text))
                            break
                        
            except Exception, e:
                
                msg = "ERROR (getAreaBedroom): " + repr(e)
                print msg
                logging.error(msg)
                area_bedroom = -1
                pass

        return area_bedroom
 
 
    
    def getAreaKitchen(self, ad):
        
        area_kitchen = -1
        if self.page != ".":
            
            try:
                
                area_objects = ad.xpath(".//table[@class = 'objects_item_props']//td")
                if area_objects != []:
                    for area_object in area_objects:
                        text = area_object.text_content().strip().replace("м2", "")
                        if text.find("Кухня") != -1:
                            area_kitchen = int(re.sub("[^0-9]", "", text))
                            break
                        
            except Exception, e:
                
                msg = "ERROR (getAreaKitchen): " + repr(e)
                print msg
                logging.error(msg)
                area_kitchen = -1
                pass

        return area_kitchen


    def getAreaLiving(self, ad):
        
        area_living = -1
        if self.page != ".":
            
            try:
                
                area_objects = ad.xpath(".//table[@class = 'objects_item_props']//td")
                if area_objects != []:
                    for area_object in area_objects:
                        text = area_object.text_content().strip().replace("м2", "")
                        if text.find("Жилая") != -1:
                            area_living = int(re.sub("[^0-9]", "", text))
                            break
                        
            except Exception, e:
                
                msg = "ERROR (getAreaLiving): " + repr(e)
                print msg
                logging.error(msg)
                area_living = -1
                pass

        return area_living


# ****************************************
# FLOORS / HOUSE TYPE
# ****************************************

    def getFlatFloor(self, ad):
        
        floor = -1
        if self.page != ".":
            
            try:
                
                floor_objects = ad.xpath(".//td[@class = 'objects_item_info_col_5']/div")
                if floor_objects != []:
                    text = floor_objects[0].text_content().strip().replace("м2", "")
                    floor = int(text.split("/")[0])
                    
            except Exception, e:
                
                msg = "ERROR (getFlatFloor): " + repr(e)
                print msg
                logging.error(msg)
                floor = -1
                pass

        return floor
    
    def getMaxFloor(self, ad):
        
        max_floor = -1
        if self.page != ".":
            
            try:
                
                floor_objects = ad.xpath(".//td[@class = 'objects_item_info_col_5']/div")
                if floor_objects != []:
                    text = floor_objects[0].text_content().strip().replace("м2", "")
                    max_floor = int( text.split(" ")[0].strip("\n").replace("\n", "").replace("/", "") )
                    
            except Exception, e:
                
                msg = "ERROR (getMaxFloor): " + repr(e)
                print msg
                logging.error(msg)
                max_floor = -1
                pass

        return max_floor
    
    def getHouseType(self, ad):
        
        house_type = "."
        if self.page != ".":
            
            try:
                
                floor_objects = ad.xpath(".//td[@class = 'objects_item_info_col_5']/div")
                if floor_objects != []:
                    text = floor_objects[0].text_content().strip().replace("м2", "")
                    house_type = re.sub("[0-9\s]", "", house_type).replace("дом", "").replace("\n", "").replace("/", "")
                    
            except Exception, e:
                
                msg = "ERROR (getHouseType): " + repr(e)
                print msg
                logging.error(msg)
                pass

        return house_type


# ****************************************
# ADDITIONAL INFO
# ****************************************

    def getInfoLift(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[0].text_content().split(":")[1].replace(" ", "").replace("\n", "").strip()
            except Exception, e:
                print "ERROR (getInfoLift): " + repr(e)
                pass

        return info
    
    def getInfoBalcon(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[1].text_content().split(":")[1].replace(" ", "").replace("\n", "").strip()
            except Exception, e:
                print "ERROR (getInfoBalcon): " + repr(e)
                pass

        return info
    
    def getInfoToilet(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[2].text_content().split(":")[1].replace(" ", "").replace("\n", "").strip()
            except Exception, e:
                print "ERROR (getInfoToilet): " + repr(e)
                pass

        return info
    
    
    def getInfoWindows(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[3].text_content().split(":")[1].replace(" ", "").replace("\n", "").strip()
            except Exception, e:
                print "ERROR (getInfoWindows): " + repr(e)
                pass

        return info
    
    def getInfoPhone(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[4].text_content().split(":")[1].replace(" ", "").replace("\n", "").strip()
            except Exception, e:
                print "ERROR (getInfoPhone): " + repr(e)
                pass

        return info
    
    def getInfoSellingStyle(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[5].text_content().strip()
            except Exception, e:
                print "ERROR (getInfoSellingStyle): " + repr(e)
                pass

        return info
    
    def getInfoSellingAge(self, ad):
        
        info = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//table[@class = 'objects_item_details']/tbody/tr")
                if info_items != []:
                    info = info_items[6].text_content().strip()
            except Exception, e:
                print "ERROR (getInfoSellingAge): " + repr(e)
                pass

        return info


# ****************************************
# REALTOR CONTACTS PROCESSING
# ****************************************

    def getRealtorMobilePhone(self, ad):
        
        phone = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//td[@class = 'objects_item_info_col_7']/div/a")
                if info_items != []:
                    for item in info_items:
                        text = item.text_content().strip()
                        code = text.split(" ")[1]
                        if code[0] == "9":
                            phone = text.replace("+7", "8").replace(" ", "-").replace("\n", "")
                            break
            except Exception, e:
                print "ERROR (getRealtorMobilePhone): " + repr(e)
                pass

        return phone 
    
    
    def getRealtorCityPhone(self, ad):
        
        phone = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//td[@class = 'objects_item_info_col_7']/div/a")
                if info_items != []:
                    for item in info_items:
                        text = item.text_content().strip()
                        if text.find(" ") != -1:
                            code = text.split(" ")[1]
                            if code[0] != "9":
                                phone = text.replace("+7", "8").replace(" ", "-").replace("\n", "")
                                break
            except Exception, e:
                print "ERROR (getRealtorCityPhone): " + repr(e) + " -- " + text
                pass

        return phone 


# ****************************************
# REALTOR COMMENT PROCESSING
# ****************************************


    
# *********************
# REALTOR IDENTITY
# *********************    
    

     
    def getRealtorID(self, ad):
        
        id = "."
        if self.page != ".":
            
            try:
                info_items = ad.xpath(".//span[contains(@class, 'objects_item_realtor_name')]/a")
                if info_items != []:
                    id = info_items[0].text_content().strip().replace("\"", "").replace("\'", "")
            except Exception, e:
                print "ERROR (getRealtorID): " + repr(e)
                pass

        return id 
    
    
    # ******************************************************
    # ********* TEXT TEXT TEXT *****************************
    # ******************************************************
    
    def getAdText(self, ad):
        
        text = "."
        if self.page != ".":
            
            try:
                text_items = ad.xpath(".//div[contains(@class, 'objects_item_info_col_comment_text no-truncate')]")
                if text_items != []:
                    
                    text = text_items[0].text_content().strip()\
                    .replace("\n", "")\
                    .replace("\"", "")\
                    .replace("\'", "")\
                    .replace("|", "I")\
                    .replace("&quot", "")\
                    .replace("&amp", "")\
                    .replace("&lt", "")\
                    .replace("&gt", "")
                    
            except Exception, e:
                print "ERROR (getAdText): " + repr(e)
                pass

        return text 
    
    
    
#     def getTextIsParticipant(self, ad):
#         
#         is_participant = 0
#         text = self.getAdText(ad)
#         try:
#             if text != u".":
#                 if text.find(u"участник акции") != -1:
#                     is_participant = 1
#         except Exception, e:
#             print "ERROR (getTextIsParticipant): " + repr(e)
#             is_participant = 0
#             pass
#         return is_participant
#     
#     def getTextPhotoCount(self, ad):
#         
#         count = 0
#         text = self.getAdText(ad)
#         try:
#             if text != u".":
#                 if text.find(u"Фото (") != -1:
#                     count = re.findall(u"\(\d+\)", text)[0].replace(u"(",u"").replace(u")", u"")
#         except Exception, e:
#             print "ERROR (getTextPhotoCount): " + repr(e)
#             count = 0
#             pass
#         return count
#     
#     
#     def getTextRealtorPhone(self, ad):
#         
#         phone = u"."
#         text = self.getAdText(ad)
#         try:
#             if text != u".":
#                 phone = re.findall("\+7\s*-*\d{3}\s*-*\d{2,}\s*-*\d{2,}\s*-*\d*|" + \
#                                    "8\s*-*\d{3}\s*-*\d{2,}\s*-*\d{2,}\s*-*\d*", text)
#                 if phone != []:
#                     phone = phone[0].replace(u" ", u"").replace(u"-", u"").replace(u"+", u"").strip()[0:11]
#                 else:
#                     phone = u"."
#         except Exception, e:
#             print "ERROR (getTextRealtorPhone): " + repr(e)
#             phone = u"."
#             pass
#         return phone
#     
#     
#     def getTextRealtorHumanName(self, ad):
#         
#         realtor_name = u"."
#         text = self.getAdText(ad)
#         
#         try:
#             
#             if text != u".":
#                 for name in self.names:
#                     if text.find(name) != -1:
#                         realtor_name = name
#                         break
#                     
#         except Exception, e:
#             
#             print "ERROR (getTextRealtorHumanName): " + repr(e)
#             realtor_name = u"."
#             pass
#         
#         return realtor_name
#     
#     
#     def getTextAreRoomsAdjacent(self, ad):
#         
#         are_rooms_adj = u"."
#         text = self.getAdText(ad)
#         try:
#             if text != u".":
#                 text = text.lower().split(u".")
#                 for sentence in text:
#                     sentence = sentence.split(u",")
#                     for phrase in sentence:
#                         if phrase.find(u"смежн") != -1:
#                             if phrase.find(u"комнат") != -1:
#                                 
#                                 # GET RID of САНУЗЕЛ
#                                 if phrase.find(u" сан") == -1:
#                                     if (phrase.find(u"узл") == -1 or phrase.find(u"узел") == -1):
#                                         
#                                         # НЕ ПРЕДЛАГАТЬ СДЕЛАТЬ СМЕЖНЫЕ КОМНАТЫ ИЗ ОДНОЙ
#                                         if phrase.find(u"можно") == -1:
#                                             are_rooms_adj = 1
#                                             break
#                         else:
#                             are_rooms_adj = 0
#                     if are_rooms_adj == 1:
#                         break
#                     
#         except Exception, e:
#             print "ERROR (getTextAreRoomsAdjacent): " + repr(e)
#             are_rooms_adj = u"."
#             pass
#         
#         return are_rooms_adj
#     
#     
#     
#     def getTextIsConserj(self, ad):
#         
#         is_conserj = "."
#         text = self.getAdText(ad)
#         try:
#             text = text.lower()
#             if text != ".":
#                 if text.find(u"консьерж") != -1 or text.find(u"конъсьерж") != -1 or text.find(u"коньсьерж") != -1:
#                     is_conserj = 1
#                 else:
#                     is_conserj = 0       
#         except Exception, e:
#             print "ERROR (getTextIsConserj): " + repr(e)
#             is_conserj = "."
#             pass
#         
#         return is_conserj
#     
#     
#     def getTextIsSecurity(self, ad):
#         
#         is_parking = "."
#         text = self.getAdText(ad)
#         try:
#             text = text.lower()
#             if text != ".":
#                 if text.find(u"охран") != -1:
#                     is_parking = 1
#                 else:
#                     is_parking = 0       
#         except Exception, e:
#             print "ERROR (getTextIsSecurity): " + repr(e)
#             is_parking = "."
#             pass
#         
#         return is_parking
#     
#     
#     def getTextIsParking(self, ad):
#         
#         is_parking = "."
#         text = self.getAdText(ad)
#         try:
#             text = text.lower()
#             if text != ".":
#                 if text.find(u"парковк") != -1 or text.find(u"паркинг") != -1:
#                     is_parking = 1
#                 else:
#                     is_parking = 0       
#         except Exception, e:
#             print "ERROR (getTextIsParking): " + repr(e)
#             is_parking = "."
#             pass
#         
#         return is_parking
#     
#     
#     def getTextIsNewBuilding(self, ad):
#         
#         is_new_building = "."
#         text = self.getAdText(ad)
#         try:
#             if text != ".":
#                 if text.lower().find(u"новострой") != -1 or text.find(u"ЖК") != -1:
#                     is_new_building = 1
#                 else:
#                     is_new_building = 0       
#         except Exception, e:
#             print "ERROR (getTextIsNewBuilding): " + repr(e)
#             is_new_building = "."
#             pass
#         
#         return is_new_building
    
    # ******************************************************
    # ********* TIME TIME TIME *****************************
    # ******************************************************
    
    
    def getTimestamp(self):
        
        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%H-%M-%S_%d-%m-%Y')
        return ts
    
    def getCurrentTime(self):
        
        ct = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M')
        return ct
    
    def getCurrentDate(self):
        
        cd = datetime.datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y')
        return cd
    
    def getAdPostingTime(self, ad):
        
        ptime = "."
        pattern = ".//span[contains(@class, 'objects_item_dt_added')]"
        try:
            
            info_items = ad.xpath(pattern)
            if info_items != []:
                
                pts = info_items[0].text_content().strip()
                ptime = re.findall("\d+:\d+", pts)
                if ptime != []:
                    ptime = ptime[0]
                else:
                    ptime = "."
                    
        except Exception, e:
            print repr(e)
            pass
        
        return ptime
    
    def getAdPostingDate(self, ad):
        
        pdate = "."
        pattern = ".//span[contains(@class, 'objects_item_dt_added')]"
        
        try:
            
            info_items = ad.xpath(pattern)
            if info_items != []:
                
                pts = info_items[0].text_content().strip()
                pdate = re.findall("\d+\.\d+\.\d+", pts)
                if pdate != []:
                    pdate = pdate[0]
                else:
                    pdate = "."
        except:
            pass
        return pdate
    
    
    
    def getAdCard(self, ad, opcode = "SELL", include_text = False):
        
        try:
            
            card = []
            # STRUCTURED REALTY FEATURES
            card.append(["Link", self.getAdLink(ad, opcode)])
            card.append(["ID", self.getAdID(ad)])
            card.append(["NRooms", self.getRoomCount(ad)])
            
            card.append(["City", self.getCity(ad)])
            card.append(["Raion", self.getRaion(ad)])
            card.append(["RaionCity", self.getRaionCity(ad)])
            
            card.append(["Street", self.getStreet(ad)])
            card.append(["House", self.getHouse(ad)])
            
            card.append(["Metro", self.getMetroStation(ad)])
            card.append(["MetroDisctrict", self.getMetroStationDistrict(ad)])
            
            mins = self.getMinutesToMetro(ad)
            bywhat = self.getByWhatToMetro(ad)
            
            card.append(["MinToMetro", mins])
            card.append(["ByWhatToMetro", bywhat])
            card.append(["MinToMetroConverted", self.getMinToMetroConverted(mins, bywhat)])
            
            card.append(["Floor", self.getFlatFloor(ad)])
            card.append(["FloorsTotal", self.getMaxFloor(ad)])
            card.append(["HouseType", self.getHouseType(ad)]) # !!!
            card.append(["AreaTotal", self.getAreaTotal(ad)])
            card.append(["AreaBedroom", self.getAreaBedroom(ad)])
            card.append(["AreaKitchen", self.getAreaKitchen(ad)])
            card.append(["AreaLiving", self.getAreaLiving(ad)])
            
            card.append(["InfoBalcon", self.getInfoBalcon(ad)])
            card.append(["InfoLift", self.getInfoLift(ad)])
            card.append(["InfoToilet", self.getInfoToilet(ad)])
            card.append(["InfoPhone", self.getInfoPhone(ad)])
            card.append(["InfoWindows", self.getInfoWindows(ad)])
            card.append(["InfoSellingStyle", self.getInfoSellingStyle(ad)])
            card.append(["InfoSellingAge", self.getInfoSellingAge(ad)])
            
            card.append(["Price", self.getPrice(ad, opcode)])
            if opcode == "SELL":
                card.append(["PriceM2", self.getPricePerSquareMeter(ad)])
            card.append(["Currency", self.getCurrency(ad, opcode)])
            if opcode != "SELL":
                card.append(["Comission", self.getPercentComission(ad, opcode)])
            
            # REALTOR INFO
            card.append(["Rltr_ID", self.getRealtorID(ad)])
            card.append(["Rltr_MobilePhone", self.getRealtorMobilePhone(ad)])
            card.append(["Rltr_CityPhone", self.getRealtorCityPhone(ad)])
#             card.append(["Text_IsCompPart", self.getTextIsParticipant(ad)])
#             card.append(["Text_PhotoCount", self.getTextPhotoCount(ad)])
            
#             # REALTOR INFO
#             card.append(["Text_RltrID", self.getRealtorID(ad)])
#             card.append(["Text_RltrHumanName", self.getTextRealtorHumanName(ad)])
#             card.append(["Text_RltrPhone", self.getAdRealtorPhone(ad)])
#             card.append(["Text_RltrPhone", self.getTextRealtorPhone(ad)])
#             card.append(["Text_IsCompPart", self.getTextIsParticipant(ad)])
#             card.append(["Text_PhotoCount", self.getTextPhotoCount(ad)])
#             
#             # REALTY FEATURES FROM TEXT
            card.append(["Text", self.getAdText(ad)])
#             card.append(["Text_RoomsAdj", self.getTextAreRoomsAdjacent(ad)])
#             card.append(["Text_Conserj", self.getTextIsConserj(ad)])
#             card.append(["Text_Security", self.getTextIsSecurity(ad)])
#             card.append(["Text_Parking", self.getTextIsParking(ad)])
#             card.append(["Text_NewBuilding", self.getTextIsNewBuilding(ad)])
            
            # DATES and TIMINGS
#             card.append(["PostingTime", self.getAdPostingTime(ad)])
#             card.append(["PostingDate", self.getAdPostingDate(ad)])
#             card.append(["CurrentTime", self.getCurrentTime()])
            card.append(["Date", self.getCurrentDate()])
            
            return card
        
        except Exception,e:
            print "ERROR (getAdCard): " + repr(e)
    
    
    
    def putAdCardsToTXT(self, txt_filename, ad_cards):
        
        try:
            
            path = os.path.dirname(txt_filename)
            if not os.path.exists(path):
                os.makedirs(path)
            
            fname = txt_filename
            fid = open(txt_filename, "w")
            lines = []
            line = u""
            
        except Exception, e:
            
            print "ERROR (putAdCardsToTXT -> files): " + repr(e)
            pass
        
        try:
            
            ad_cards_num = len(ad_cards)
            for i in range(ad_cards_num):
                
                if i % 50 == 0:
                    print str(i) + " ad cards out of " + str(ad_cards_num) + " were processed!"
                    
                ad_card = ad_cards[i]
                
                try:
                
                    if i == 0:
                        line = u""
                        for j in range(len(ad_card)):
                            if j != len(ad_card) - 1:
                                line = line + str(ad_card[j][0]) + u"|"
                            else:
                                line = line + str(ad_card[j][0]) + u"\n"
                        lines.append(codecs.encode(line, 'utf8'))
                        
                except Exception, e:
                    print "ERROR (putAdCardsToTXT -> accumulating lines - 1): " + repr(e)
                    pass
                
                
                try:
                    line = u""
                    for j in range(len(ad_card)):
                        if j != len(ad_card) - 1:
                            line = line + str(ad_card[j][1]) + "|"
                        else:
                            line = line + str(ad_card[j][1]) + "\n"
                    lines.append(codecs.encode(line, 'utf8'))
                except Exception, e:
                    print "ERROR (putAdCardsToTXT -> accumulating lines - 2): " + repr(e)
                    pass
            
            try:
                fid.writelines(lines)
                print "Data saved as " + fname
                fid.close()
            
            except Exception, e:
                print "ERROR (putAdCardsToTXT -> writing files): " + repr(e)
                fid.close()     
        
        except Exception, e:
            print "ERROR (putAdCardsToTXT): " + repr(e)
            fid.close()
            pass
        
        return
    
    
    def joinResultTXT(self, dir, date_marker, result_filename_pattern = "RESULT_"):
        
        
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        filenames = glob.glob1(dir, result_filename_pattern + "[0-9]*.txt")
        result_filename = result_filename_pattern + "ALL_" + dir.split("\\")[-2] + date_marker + ".txt"
        join_fid = open( os.path.join(dir, result_filename), "w")
        
        for i in range(len(filenames)):
            
            filenames[i] = os.path.join(dir, filenames[i])
            fid = open( filenames[i] )
            lines = fid.readlines();
            join_fid.writelines(lines)
            fid.close()
            print "Result file " + os.path.basename(filenames[i]) + " appended to " + result_filename
            
        join_fid.close()
        
        return
        
        
    def updateCurrentDataFolder(self, dir, current_data_folder, result_filename_pattern = "RESULT_*"):
        
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        if not os.path.exists(current_data_folder):
            os.makedirs(current_data_folder)
    
        filenames = glob.glob1(dir, result_filename_pattern)
        old_filenames = []
        new_filenames = []
        
        print filenames
        
        for i in range(len(filenames)):
            
            old_filenames.append(os.path.join(dir, filenames[i]))
            if old_filenames[i].find("ALL") != -1:
                new_filenames.append(os.path.join(current_data_folder, "RESULT_ALL.txt"))
            else:
                new_filenames.append(os.path.join(current_data_folder, filenames[i]))
            
            import shutil
            shutil.copyfile(old_filenames[i], new_filenames[i])
        
        
    
    def putPageAdsFromFileToExcel(self, excel_filename, page_filenames, opcode = "SELL", enc = "cp1251"):
        
        ads_cards_all = []
        for fname in page_filenames:
            print "Processing file " + os.path.basename(fname)
            self.setPageFromFile(fname, enc)
            for ad in self.ads:
                ads_cards_all.append(self.getAdCard(ad, opcode, include_text = False))
        
        self.putAdCardsToExcel(excel_filename, ads_cards_all)
        print "\n"
        return
    
    
    def putPageAdsFromFileToTXT(self, txt_filename, page_filenames, opcode = "SELL", enc = "utf8"):
        
        ads_cards_all = []
        try:
            for fname in page_filenames:
                print "Processing file " + os.path.basename(fname)
                self.setPageFromFile(fname, enc)
                for ad in self.ads:
                    ads_cards_all.append(self.getAdCard(ad, opcode, include_text = False))
                
            self.putAdCardsToTXT(txt_filename, ads_cards_all)
            print "\n"
            
        except Exception, e:
            print "ERROR (putPageAdsFromFileToTXT):" + repr(e)
            
        return


# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************


#  
# testpage_fname = "C:\\CIAN_DATA\\MSK\\SELL\\2015-03-03___18-15\\page_0_1.txt"
#   
# cp = CianParser()
# cp.setPageFromFile(testpage_fname)
# 
# for i in range(len(cp.ads)):
#     ad = cp.ads[i]
#     print i, " --> ", cp.getAdText(ad)