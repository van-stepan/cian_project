# -*- coding: utf-8 -*-

import psycopg2
import logging
import re
import numpy


columns_dictionary = {"Link" :  "varchar",
                      "ID" :  "varchar",
                      "NRooms" :  "varchar",
                      
                      "City" :  "varchar",
                      "Raion" :  "varchar",
                      "RaionCity" :  "varchar",
                      "Street" :  "varchar",
                      "House" :  "varchar",
                      
                      "Metro" :  "varchar",
                      "MetroDisctrict" :  "varchar",
                      "MinToMetro" :  "integer",
                      "ByWhatToMetro" :  "varchar",
                      "MinToMetroConverted" :  "integer",
                      
                      "Floor" :  "integer",
                      "FloorsTotal" :  "integer",
                      "HouseType" :  "varchar",
                      
                      "AreaTotal" :  "integer",
                      "AreaBedroom" :  "integer",
                      "AreaKitchen" :  "integer",
                      "AreaLiving" :  "integer",
                      
                      "InfoBalcon" :  "varchar",
                      "InfoLift" :  "varchar",
                      "InfoToilet" :  "varchar",
                      "InfoPhone" :  "varchar",
                      "InfoWindows" :  "varchar",
                      "InfoSellingStyle" :  "varchar",
                      "InfoSellingAge" :  "varchar",
                      
                      "Price" :  "integer",
                      "PriceM2" :  "integer",
                      "Currency" :  "varchar",
                      
                      "Rltr_ID" :  "varchar",
                      "Rltr_MobilePhone" :  "varchar",
                      "Rltr_CityPhone" :  "varchar",
                      
                      "Text" : "varchar",
                      
                      "PostingTime" :  "varchar",
                      "PostingDate" :  "varchar",
                      "CurrentTime" :  "varchar",
                      "CurrentDate" :  "varchar"}

columns_list =      [["Link", "varchar"], 
                      ["ID", "varchar"], 
                      ["NRooms", "varchar"], 
                      
                      ["City", "varchar"], 
                      ["Raion", "varchar"], 
                      ["RaionCity", "varchar"], 
                      ["Street", "varchar"], 
                      ["House", "varchar"], 
                      
                      ["Metro", "varchar"], 
                      ["MetroDisctrict", "varchar"], 
                      ["MinToMetro", "varchar"], 
                      ["ByWhatToMetro", "varchar"], 
                      ["MinToMetroConverted", "varchar"], 
                      
                      ["Floor", "varchar"], 
                      ["FloorsTotal", "varchar"], 
                      ["HouseType", "varchar"], 
                      
                      ["AreaTotal", "varchar"], 
                      ["AreaBedroom", "varchar"], 
                      ["AreaKitchen", "varchar"], 
                      ["AreaLiving", "varchar"], 
                      
                      ["InfoBalcon", "varchar"], 
                      ["InfoLift", "varchar"], 
                      ["InfoToilet", "varchar"], 
                      ["InfoPhone", "varchar"], 
                      ["InfoWindows", "varchar"], 
                      ["InfoSellingStyle", "varchar"], 
                      ["InfoSellingAge", "varchar"], 
                      
                      ["Price", "varchar"], 
                      ["PriceM2", "varchar"], 
                      ["Currency", "varchar"], 
                      
                      ["Rltr_ID", "varchar"], 
                      ["Rltr_MobilePhone", "varchar"], 
                      ["Rltr_CityPhone", "varchar"], 
                      
                      ["Text", "varchar"], 
                      
                      ["PostingTime", "varchar"], 
                      ["PostingDate", "varchar"], 
                      ["CurrentTime", "varchar"], 
                      ["CurrentDate", "varchar"]]


class PSQLHandler():
    
    def __init__(self, host = 'localhost', port = '5432', dbname = 'cian', user = 'postgres', password = '130130130'):
        
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connectDB()
        
        return
    
    def setHost(self, host):
        
        self.host = host
        
    def setPort(self, port):
        
        self.port = port
        
    def setDB(self, dbname):
        
        self.dbname = dbname
        
    def setActiveTable(self, active_table):
        
        self.active_table = active_table
        
        
    def connectDB(self):
        
        try:
    
            conn=psycopg2.connect("dbname='" + self.dbname + "' user='" + self.user + "' password='" + self.password + "'")
            conn.set_isolation_level(0)
            self.conn = conn
            print "Connection to PosgreSQL was successful!"
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.connectDB): " + repr(e)
            logging.error(msg)
            print msg
            pass

        return
    
    
    def execute(self, query, silent = False, return_response = True, isolation_level = 0):
        
        if self.conn == None:
            print "ERROR (PSQLHandler.execute): no connection handler was created"
            return None
        
        try:
            self.conn.set_isolation_level(isolation_level)
            cur = self.conn.cursor()
            cur.execute(query)
            if not silent:
                print "SUCCESS --> " + query
            
            if return_response == True:
                
                try:
                    rows = cur.fetchall()
                    return rows
                except:
                    return []
                    pass
            else:
                return
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.execute): " + repr(e)
            logging.error(msg)
            print msg
            pass
            
    def getColumnsListFromCSV(self, filename, dlm = "|"):
        
        first_line = open(filename).readlines()[0]
        raw_columns_list = first_line.strip().replace(" ", "").replace("\n", "").split(dlm)
        columns_list = []
        
        for item in raw_columns_list:
            columns_list.append([item, "varchar"])
            
        return columns_list
        
        
    def getCreateTableQuery(self, dest_table, columns_list):
        
        create_table_query = "CREATE TABLE " + dest_table + " (<vars>);"
        
        for i in range(len(columns_list)):
            
            if i != len(columns_list) - 1:
                create_table_query = create_table_query.replace("<vars>", columns_list[i][0] + " " + columns_list[i][1] + ", <vars>")
            else:
                create_table_query = create_table_query.replace("<vars>", columns_list[i][0] + " " + columns_list[i][1])
                
        return create_table_query


    def getLoadFromCsvQuery(self, dest_table, filename, dlm = "|"):
        
        load_from_csv_query = "COPY " + dest_table + " FROM '" + filename + "' (FORMAT CSV, DELIMITER '" + dlm + "', HEADER 1, ENCODING 'UTF8');"
        return load_from_csv_query
    
    
    # COPY just those columns from FILENAME which are present in columns_list
    def getLoadFromCsvQueryPartial(self, dest_table, filename, columns_list, dlm = "|"):
        
        load_from_csv_query = "COPY " + dest_table + " FROM '" + filename + "' (FORMAT CSV, DELIMITER '" + dlm + "', HEADER 1, ENCODING 'UTF8');"
        
        return load_from_csv_query
    
    def getDeduplicatedTableSimple(self, src_table, dest_table = None, silent = False):
        
        if dest_table == None:
            query = "CREATE TABLE _temp_ AS SELECT DISTINCT * FROM " + src_table + ";"
            self.execute(query, silent)
            query = "DROP TABLE " + src_table + ";"
            self.execute(query, silent)
            query = "CREATE TABLE " + src_table + " AS SELECT * FROM _temp_;"
            self.execute(query, silent)
            query = "DROP TABLE _temp_;"
            self.execute(query, silent)
        else:
            query = "CREATE TABLE " + dest_table + " AS SELECT * FROM " + src_table + ";"
            self.execute(query)
            
    def loadCIANResultIntoPSQL(self, dest_table, filename, silent = False):
        
        try:
            
            file_columns_list = self.getColumnsListFromCSV(filename)
            print "NUMBER of FILE COLUMNS: " + str(len(file_columns_list))
            query = self.getCreateTableQuery(dest_table, file_columns_list)
            self.execute(query, silent)
            query = self.getLoadFromCsvQuery(dest_table, filename)
            self.execute(query, silent)
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.loadCIANResultIntoPSQL): " + repr(e)
            logging.error(msg)
            print msg
        
        return
    
    
    def getTableColumnsList(self, src_table, silent = False):
        
        try:
    
            query = "select column_name, data_type, character_maximum_length from INFORMATION_SCHEMA.COLUMNS where table_name = '" + src_table + "';"
            rows = self.execute(query, silent)
            return map(list, rows)
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.getTableColumnsList): " + repr(e)
            logging.error(msg)
            print msg
        
        return
    
    
    def getFullColumnsListByTableArray(self, src_table_array, silent = False):
        
        full_columns_list = []
        for src_table in src_table_array:
            
            table_columns_list = self.getTableColumnsList(src_table, silent)
            table_columns_list = map(tuple, table_columns_list)
            full_columns_list_buf = map(tuple, full_columns_list)
            
            full_columns_list = full_columns_list + list(set(table_columns_list) - set(full_columns_list_buf))
        
        full_columns_list = map(list, full_columns_list)
        
        return full_columns_list
    
    
    def getTableArrayByPattern(self, table_name_pattern = "[a-zA-z0-9]*", silent = False):
        
        # Returns array of list [table_schema, table_name]
        
        try:
    
            query = "SELECT table_schema,table_name FROM information_schema.tables;";
            rows = self.execute(query, silent)
            regexp = re.compile(table_name_pattern)
           
            return [row[1] for row in rows if regexp.search(row[1])]
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.getTableArrayByPattern): " + repr(e)
            logging.error(msg)
            print msg
        
        return
        
        
        
        
    def isColumnExistsInTable(self, column_name = "", table_name = "", silent = False):
        
        try:
    
            query = "select column_name from information_schema.columns where table_name = '" + table_name + "' and column_name = '" + column_name + "';";
            rows = self.execute(query, silent)
            if not rows:
                return False
            else:
                return True
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.isColumnExistsInTable): " + repr(e)
            logging.error(msg)
            print msg
        
        return
  
  
    
    def standardizeTableColumns(self, table_name_pattern = "*", silent = False):
        
        array = self.getTableArrayByPattern(table_name_pattern)
        full_columns_list = [item[0] for item in self.getFullColumnsListByTableArray(array)]
        
        try:
            
            for table in array:
                for column in full_columns_list:
                    
                    if not self.isColumnExistsInTable(column, table, silent = True):
                        
                        query = "ALTER TABLE " + table + " ADD COLUMN " + column + " varchar;";
                        self.execute(query, silent)
                        query = "UPDATE " + table + " SET " + column + " = '.';";
                        self.execute(query, silent)
                        
                        print "Column " + column + " added to a table " + table
             
        except Exception, e:
             
            msg = "ERROR (PSQLHandler.standardizeTableColumns): " + repr(e)
            logging.error(msg)
            print msg
        
        return
    
    
    
    def unionTables(self, src_table_array, result_table_name, remove_duplicates = False, silent = False):
        
        try:
            
            if remove_duplicates:
                union_modifier = " all "
            else:
                union_modifier = ""
            
            query = "create table " + result_table_name + " as select * from "
            for i in range(len(src_table_array)):
                table = src_table_array[i]
                if i != len(src_table_array) - 1:
                    query = query + table + " union " + union_modifier + " select * from "
                else:
                    query = query + table + ";"

            rows = self.execute(query, silent)
            return rows
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.unionTables): " + repr(e)
            logging.error(msg)
            print msg
        
        return
    
    
    def getColumnType(self, column_name, table_name, silent = False):
        
        try:
            
            if self.isColumnExistsInTable(column_name, table_name, silent = False):
                
                query = "select data_type from information_schema.columns where table_name = '" + table_name + "' and column_name = '" + column_name + "';"
                rows = self.execute(query)
                if rows != []:
                    if list(rows[0]) != []:
                        return rows[0][0]
                else:
                    return None
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.getColumnType): " + repr(e)
            logging.error(msg)
            print msg
        
        return 
        
    
    def prettifyTableColumns(self, table_name, silent = False):
        
        try:
            
            column_data = [("price", "bigint"), ("pricem2", "bigint"), ("current_date", "date")]
            
            for item in column_data:
                
                column_name = item[0]
                new_column_type = item[1]
                
                if self.isColumnExistsInTable(column_name, table_name):
                    
                    current_column_type = psql.getColumnType(column_name, table_name)
                    
                    if current_column_type != new_column_type:
                        
                        query = "update " + table_name + " set " + column_name + " = replace(" + column_name + ", ' ', '');"
                        self.execute(query)
                        
                        if new_column_type.find('date') == -1:
                            
                            query = "delete from " + table_name + " where " + column_name + " = 'Price';"
                            self.execute(query)
                            query = "delete from " + table_name + " where " + column_name + " = '';"
                            self.execute(query)
                            query = "alter table " + table_name + " alter column " + column_name + " type " + new_column_type\
                                     + " using " + column_name + "::" + new_column_type + ";"
                            self.execute(query)
                            
                        else:
                            
                            query = "delete from " + table_name + " where " + column_name + " = '';"
                            self.execute(query)
                            query = "update " + table_name + " set " + column_name + " = to_date(" + column_name + ", 'YYYY-MM-DD');"
                            self.execute(query)
                            
                            
            
        except Exception, e:
            
            msg = "ERROR (PSQLHandler.prettifyTableColumns): " + repr(e)
            logging.error(msg)
            print msg
        
        return 
    
    
    
#     def createStatsTable(self, result_table):
#         
#         table_array = self.getTableArrayByPattern("raw*")
#         self.unionTables(table_array, "current_main")
#         
#         try:
#                 
#             query = "select nrooms, avg from information_schema.columns where table_name = '" + table_name + "' and column_name = '" + column_name + "';"
#             rows = self.execute(query)
#             if rows != []:
#                 if list(rows[0]) != []:
#                     return rows[0][0]
#             else:
#                 return None
#             
#         except Exception, e:
#             
#             msg = "ERROR (PSQLHandler.createStatsTable): " + repr(e)
#             logging.error(msg)
#             print msg
#         
#         return
        
        
    
    def dropTablesByPattern(self, table_name_pattern = "*", silent = False):
        
        try:
            
            table_array = self.getTableArrayByPattern(table_name_pattern)
            for table_name in table_array:
                query = "DROP table " + table_name + ";"
                self.execute(query, silent)
             
        except Exception, e:
             
            msg = "ERROR (PSQLHandler.loadCIANResultIntoPSQL): " + repr(e)
            logging.error(msg)
            print msg
         
        return

psql = PSQLHandler()
# 
# psql.standardizeTableColumns("test")
# 
# print len(psql.getFullColumnsListByTableArray(['test'])), len(psql.getFullColumnsListByTableArray(['test_1']))

table = "raw_2015_03_06___00_19_buf"
psql.prettifyTableColumns(table)
#  
# psql.dropTablesByPattern(table_name_pattern)
#  
# print len(psql.getTableArrayByPattern(table_name_pattern))
#  
# dest_table = "raw_data"
# filename = "C:\\CIAN_DATA\\MSK\\SELL\\2015-02-23___01-19\\RESULT_0.txt"

# file_columns_list = psql.getColumnsListFromCSV(filename)
# query = psql.getCreateTableQuery(dest_table, file_columns_list)
# psql.execute(query)
# query = psql.getLoadFromCsvQuery(dest_table, filename)
# psql.execute(query)
#  
# psql.getDeduplicatedTableSimple(dest_table)
