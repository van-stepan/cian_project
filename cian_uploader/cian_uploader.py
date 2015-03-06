# -*- coding: utf-8 -*-

import os
import lxml.html as html
from lxml import etree
import urllib2
import glob
import codecs
import math
from support import dicts
import datetime

class CianPageUploader:
    
    def __init__(self, dir, url_pattern = None, nrooms = [1], page_file_pattern = "page"):
        
        self.dir = dir
        self.nrooms = nrooms
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.file_pattern = page_file_pattern
        if url_pattern == None:
            self.url_pattern = "http://www.cian.ru/cat.php?deal_type=1&obl_id=1&type=4&room<nrooms>=1&p=<npage>"
        else:
            self.url_pattern = url_pattern
        
    
    
    def getMaxPageNumber(self, room_count):
    
        max_page_number = -1
        url = self.url_pattern.replace("<nrooms>", str(room_count)).replace("<npage>", "1")
        page = urllib2.urlopen(url).read()
        doc = html.document_fromstring(page)
        
        try:
            find_total_ads_count = etree.XPath("//span[@class = 'objects_list_title_site_selected']")
        except Exception, e:
            print repr(e)
        
        total_ads_count = int(find_total_ads_count(doc)[0].text)
        max_page_number = int(math.ceil(total_ads_count / 25.0))
        
        return max_page_number
    
    
    
    def uploadPages(self, nattempts = 5):
        
        print "Uploading pages from CIAN started...\n"
        
        for i in self.nrooms:
            try:
                
                max_page_number = self.getMaxPageNumber(i)
                print "NUMBER of PAGES in ROOMS=" + str(i) + ": " + str(max_page_number)
                
                for j in range(1, max_page_number + 1):
                    
                    attempt = nattempts
                    while attempt > 0:
                        try:
                            page = urllib2.urlopen(self.url_pattern.replace("<nrooms>", str(i)).replace("<npage>", str(j)), 
                                                   timeout = 5).read()
                                                   
                            filename = os.path.join(self.dir, self.file_pattern + "_" + str(i) + "_" + str(j) + ".txt")
                            fid = open(filename, 'w')
                            fid.write(page)
                            fid.close()
                    
                            print "FILE " + os.path.basename(filename) + " WAS SUCCESSFULLY PROCESSED"
                            
                            attempt = 0
                            
                        except Exception, e:
                            print "ERROR (CianPageUploader.uploadPages) --> " + str(attempt - 1) + " attempts remained : " + repr(e)
                            attempt = attempt - 1
                    
            except Exception, e:
                
                print "ERROR: (CianPageUploader.uploadPages)" + repr(e)
                pass



# date_marker = datetime.datetime.now().strftime("%Y-%m-%d___%H-%M")
# dir = os.path.join(dicts.dirs['msk']['sell'], date_marker)
# 
# page_file_pattern = "page"
# url_pattern = dicts.url_patterns['msk']['sell']
# 
# cu = CianPageUploader(dir, page_file_pattern, url_pattern)
# cu.uploadPages()