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

def mergeRoomwiseFiles(dir, file_pattern, dlm = "|"):
    
    raw_files = glob.glob1(dir, file_pattern + "*")
    files = []
    for i in range(len(raw_files)):
        if raw_files[i].find("ALL") == -1:
            files.append( os.path.join(dir, raw_files[i]) )
        
    result_file = os.path.join(dir, file_pattern + "ALL.txt")
    lines = []
    
    for file in files:
        
        fid = open(file)
        partial_lines = fid.readlines()
        fid.close()
        
        partial_lines_buf = []
        nfields = partial_lines[0].count(dlm)
        
        flag = 0
        for i in range(len(partial_lines)):
            
            if flag == 1:
                flag = 0
                continue
            
            current_nfields = partial_lines[i].count(dlm)
            
            if current_nfields != nfields and i < len(partial_lines) - 1:
                partial_lines_buf.append( partial_lines[i].replace("\n", "") + partial_lines[i + 1] )
                flag = 1
            else:
                partial_lines_buf.append( partial_lines[i] )
            
        
        lines.extend(partial_lines_buf)
        
    fid = open(result_file, 'w')
    fid.writelines(lines)
    fid.close()
    
    return result_file
    

def createAggregateUploadResult(dir, file_pattern):
    
    result_file = os.path.join(dir, file_pattern + "ALL.txt")
    if not os.path.exists(result_file):
        mergeRoomwiseFiles(dir, file_pattern)
        

def getNumberOfFieldsFromFile(filename, delimiter = "|"):
    
    fid = open(filename)
    line = fid.readlines()[0]
    fields = line.split(delimiter)
    
    number_of_fields = len(fields)
    
    return number_of_fields


def getFieldNumber(header, field, delimiter = "|"):
    
    nfield = -1
    
    fields = header.split(delimiter)
    for i in range(len(fields)):
        if fields[i].strip() == field:
            nfield = i
            break
    
    return nfield


def purgeTextFromResult(dir, total_result_filename, delimeter = "|"):
    
    
    new_total_result_filename = total_result_filename.replace(".txt", "_NOTEXT.txt")
    
    result_filepath = os.path.join(dir, total_result_filename)
    new_result_filepath = os.path.join(dir, new_total_result_filename)
    
    if not os.path.exists(new_result_filepath):
    
        fid = open(result_filepath)
        lines = fid.readlines()
        fid.close()
        
        ntextfield = getFieldNumber(lines[0], "Text")
        print "Starting purging lines..."
        
        for i in range(len(lines)):
    
            new_line = ""
            old_line = lines[i]
            old_line_array = old_line.split(delimeter)
            for j in range(len(old_line_array)):
                if j != ntextfield:
                    if j == 1:
                        new_line = old_line_array[j]
                    else:
                        new_line = new_line + "|" + old_line_array[j]
            lines[i] = new_line
         
        fid_new = open(new_result_filepath, 'w')
        lines = fid_new.writelines(lines)
        fid_new.close()


def getDatepartsFromDirName(dir):
    
    dir = os.path.basename(dir)
    dateparts = dir.split("___")
    
    date = dateparts[1]
    time = dateparts[2]
    
    return [date, time]

def getDateFromDirName(dir):
    
    dir = os.path.basename(dir)
    dateparts = dir.split("___") 
    date = dateparts[1].split("-")
    
    return date

def getTimeFromDirName(dir):
    
    dir = os.path.basename(dir)
    dateparts = dir.split("___") 
    time = dateparts[2].split("-")
    
    return time



def getImmediateSubdirectories(a_dir):
    
    subdirs = []
    for name in os.listdir(a_dir):
        if os.path.isdir(os.path.join(a_dir, name)):
            subdirs.append(os.path.join(a_dir, name))
            
    return subdirs

# Dodelat!
def createAggregatedFolderResult(basedir, aggregated_result_filename):
    
    subdirs = getImmediateSubdirectories(basedir)
    
    fid_all = open( os.path.join(basedir, "RESULT_AGGREGATED_FROM_FOLDERS.txt"), "w" )
    all_lines = []
    
    for subdir in subdirs:
        
        fname = os.path.join(basedir, os.path.join(subdir, aggregated_result_filename))
        if os.path.exists(fname):
        
            fid = open( fname, "r" )
            lines = fid.readlines()
            fid.close()
            
            all_lines.extend(lines)
        
    fid_all.writelines(all_lines)
    fid_all.close()
        
# dir = "C:\\cian\\DATA\\MSK\\SELL\\___2014-08-26___16-43"
# file_pattern = "RESULT_"
# 
# createAggregateUploadResult(dir, file_pattern)
# purgeTextFromResult(dir, file_pattern + "ALL.txt")
# basedir = "C:\\cian\\DATA\\MSK\\SELL"
# aggregated_result_filename = "RESULT_ALL_NOTEXT.txt"
# createAggregatedFolderResult(basedir, aggregated_result_filename)
