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

import support.lists as lists
import support.utilities as utilities
import support.dicts as dicts
import support.psql as psql

import cian_parser.cian_parser
import cian_uploader.cian_uploader
 
 
names = lists.names
metro_stations = lists.metro_stations
 
class CianProcessingManager:
    
    def __init__(self, baseline_dir = "C:\\cian_pages",
                       destination_file_pattern = "page",
                       excel_fname_pattern = "RESULT_",
                       region = "MSK",
                       deal_type = "RENT"):
        
        self.url_pattern_rent = dicts.url_patterns['msk']['rent']
        self.url_pattern_sell = dicts.url_patterns['msk']['sell']
        self.url_pattern_rent_region = dicts.url_patterns['msk_region']['rent']
        self.url_pattern_sell_region = dicts.url_patterns['msk_region']['sell']
        
        
        self.baseline_dir = baseline_dir
        self.destination_file_pattern = destination_file_pattern
        self.excel_fname_pattern = excel_fname_pattern
        self.region = region
        self.deal_type = deal_type
        self.url_pattern = url_pattern
        
        return
    
    def getNewUploadDir(self):
        
        from time import localtime, strftime
        timestamp = strftime("%d-%m-%Y %H-%M", localtime())
        
        full_baseline_dir = self.baseline_dir + "_" + str.lower(self.deal_type)
        dir = os.path.join(full_baseline_dir, self.region + " (" + timestamp + ")\\")
        
        return dir
    
    def getExistingDirs(self):
    
        dir_pattern = os.path.join(self.region + "\\*")
        full_baseline_dir = self.baseline_dir + "_" + str.lower(self.deal_type)
        dir_names = glob.glob1(self.baseline_dir, dir_pattern)
        
        return dir_names
    
    def uploadNewPages(self):
        
        dir = self.getNewUploadDir()
        
        uploader = cian_uploader.cian_uploader.CianPageUploader(dir, self.destination_file_pattern, self.url_pattern)
        uploader.uploadPages()
    
    
# ************************************************************************************************
# ************************************************************************************************
# ************************************************************************************************


import logging
logging.basicConfig(filename='C:\\CIAN_DATA\\LOG.TXT', level=logging.ERROR)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.warning('is when this event was logged.')

nrooms = [0,1,2,3,4,5,6]

date_marker = datetime.datetime.now().strftime("%Y-%m-%d___%H-%M")
dir = os.path.join(dicts.dirs['msk']['sell'], date_marker)
url_pattern = dicts.url_patterns['msk']['sell']

opcode = "SELL"


# UPLOADING
 
uploader = cian_uploader.cian_uploader.CianPageUploader(dir, url_pattern, nrooms)
uploader.uploadPages()
   
# # PARSING
    
page_file_pattern = dicts.page_file_pattern
resfile_part_pattern = dicts.resfile_part_pattern
     
cp = cian_parser.cian_parser.CianParser()
for k in nrooms:
                 
    try:
        page_filenames_all = []
        page_filenames = glob.glob1(dir, page_file_pattern + "_" + str(k) + "*.txt")
        print "There are " + str(len(page_filenames)) + " " + page_file_pattern +  "* files in dir " + dir
        for i in range(len(page_filenames)):
            page_filenames[i] = os.path.join(dir, page_filenames[i])
            page_filenames_all.append(page_filenames[i])
    except:
        pass
                    
                    
    if page_filenames_all != []:
        txt_filename = os.path.join(dir, resfile_part_pattern + str(k) + ".txt")
        cp.putPageAdsFromFileToTXT(txt_filename, page_filenames_all, opcode)
             
             
    for page_filename in page_filenames_all:
        print page_filename
             
             
    try:
        for page_filename in page_filenames_all:
            os.remove(page_filename)
    except:
        pass

 
result_file = utilities.mergeRoomwiseFiles(dir, resfile_part_pattern)
# 
# dir = "C:\\CIAN_DATA\\MSK\\SELL\\2015-03-06___00-19" # raw_2015_03_06___00_19
# result_file = os.path.join(dir, "RESULT_ALL.txt")
psqlh = psql.PSQLHandler()

dest_table = "raw_" + os.path.basename(dir).replace("-", "_")
print dir, result_file
psqlh.loadCIANResultIntoPSQL(dest_table, result_file)

# psqlh = psql.PSQLHandler()
#    
# a_dir = "C:\\CIAN_DATA\\MSK\\SELL\\"
# def get_immediate_subdirectories(a_dir):
#     return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
#         if os.path.isdir(os.path.join(a_dir, name))]
#         
# for dir in get_immediate_subdirectories(a_dir):
#      
#     result_file = utilities.mergeRoomwiseFiles(dir, resfile_part_pattern)
#     dest_table = "raw_" + os.path.basename(dir).replace("-", "_")
#     print dir, result_file
#     psqlh.loadCIANResultIntoPSQL(dest_table, result_file)