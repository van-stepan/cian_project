# -*- coding: utf-8 -*-

import psycopg2
import logging
import re
import os
import numpy as np
from scipy import stats


columns_dictionary_total = {"Link" :  "varchar",
                      "ID" :  "varchar",
                      "NRooms" :  "varchar",
                      
                      "City" :  "varchar",
                      "Raion" :  "varchar",
                      "RaionCity" :  "varchar",
                      "Street" :  "varchar",
                      "House" :  "varchar",
                      
                      "Metro" :  "varchar",
                      "MetroDisctrict" :  "varchar",
                      "MinToMetro" :  "bigint",
                      "ByWhatToMetro" :  "varchar",
                      "MinToMetroConverted" :  "bigint",
                      
                      "Floor" :  "bigint",
                      "FloorsTotal" :  "bigint",
                      "HouseType" :  "varchar",
                      
                      "AreaTotal" :  "bigint",
#                       "AreaBedroom" :  "bigint",
                      "AreaKitchen" :  "bigint",
                      "AreaLiving" :  "bigint",
                      
                      "InfoBalcon" :  "varchar",
                      "InfoLift" :  "varchar",
                      "InfoToilet" :  "varchar",
                      "InfoPhone" :  "varchar",
                      "InfoWindows" :  "varchar",
                      "InfoSellingStyle" :  "varchar",
                      "InfoSellingAge" :  "varchar",
                      
                      "Price" :  "bigint",
                      "PriceM2" :  "bigint",
                      "Currency" :  "varchar",
                      
                      "Rltr_ID" :  "varchar",
                      "Rltr_MobilePhone" :  "varchar",
                      "Rltr_CityPhone" :  "varchar",
                      
                      "Text" : "varchar",
                      
#                       "PostingTime" :  "varchar",
#                       "PostingDate" :  "varchar",
#                       "CurrentTime" :  "varchar",
                      "Date" :  "varchar"}

columns_list_total =      [["Link", "varchar"], 
                      ["ID", "varchar"], 
                      ["NRooms", "varchar"], 
                      
                      ["City", "varchar"], 
                      ["Raion", "varchar"], 
                      ["RaionCity", "varchar"], 
                      ["Street", "varchar"], 
                      ["House", "varchar"], 
                      
                      ["Metro", "varchar"], 
                      ["MetroDisctrict", "varchar"], 
                      ["MinToMetro", "bigint"], 
                      ["ByWhatToMetro", "varchar"], 
                      ["MinToMetroConverted", "bigint"], 
                      
                      ["Floor", "bigint"], 
                      ["FloorsTotal", "bigint"], 
                      ["HouseType", "varchar"], 
                      
                      ["AreaTotal", "bigint"], 
#                       ["AreaBedroom", "bigint"], 
                      ["AreaKitchen", "bigint"], 
                      ["AreaLiving", "bigint"], 
                      
                      ["InfoBalcon", "varchar"], 
                      ["InfoLift", "varchar"], 
                      ["InfoToilet", "varchar"], 
                      ["InfoPhone", "varchar"], 
                      ["InfoWindows", "varchar"], 
                      ["InfoSellingStyle", "varchar"], 
                      ["InfoSellingAge", "varchar"], 
                      
                      ["Price", "bigint"], 
                      ["PriceM2", "bigint"], 
                      ["Currency", "varchar"], 
                      
                      ["Rltr_ID", "varchar"], 
                      ["Rltr_MobilePhone", "varchar"], 
                      ["Rltr_CityPhone", "varchar"], 
                      
                      ["Text", "varchar"], 
                      
#                       ["PostingTime", "varchar"], 
#                       ["PostingDate", "varchar"], 
#                       ["CurrentTime", "varchar"], 
                      ["Date", "varchar"]]


# PostgreSQL Handler

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
            try:
                columns_list.append([item, columns_dictionary_total[item]])
            except:
                columns_list.append([item, "varchar"])
                print "CAUTION (getColumnsListFromCSV): " + item + " type set to varchar"
            
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
    
    
    
    def unionTables(self, src_table_array, 
                    result_table_name, 
                    result_columns_list = [], 
                    remove_duplicates = True, 
                    silent = False):
        
        if result_columns_list == []:
            result_columns_list = [col[0] for col in self.getFullColumnsListByTableArray(src_table_array)]
        
        try:
            
            if remove_duplicates:
                union_modifier = ""
            else:
                union_modifier = " all "
            
            column_order_string = ""
            for i in range(len(result_columns_list)):
                col = result_columns_list[i]
                if i == 0:
                    column_order_string = column_order_string + col
                else:
                    column_order_string = column_order_string + ", " + col
            
            if result_table_name in src_table_array:
                
                query = "create table _temp_ as select " + column_order_string + " from " + result_table_name + \
                        " union " + union_modifier + " select " + column_order_string + " from "
                        
                for i in range(len(src_table_array)):
                    table = src_table_array[i]
                    if i != len(src_table_array) - 1:
                        query = query + table + " union " + union_modifier + " select " + column_order_string + " from "
                    else:
                        query = query + table + ";"
                        
                rows = self.execute(query, silent)
                
                query = "select * into " + result_table_name + " from _temp_;"
                self.execute(query, silent)
                
                query = "drop table _temp_;"
                self.execute(query, silent)
                
                return rows
            
            else:
                
                query = "create table " + result_table_name + " as select " + column_order_string + " from "
                        
                for i in range(len(src_table_array)):
                    table = src_table_array[i]
                    if i != len(src_table_array) - 1:
                        query = query + table + " union " + union_modifier + " select " + column_order_string + " from "
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
            
            column_data = [("price", "bigint"), ("pricem2", "bigint"), ("date", "date")]
            
            for item in column_data:
                
                column_name = item[0]
                new_column_type = item[1]
                
                if self.isColumnExistsInTable(column_name, table_name):
                    
                    current_column_type = self.getColumnType(column_name, table_name)
                    
                    if current_column_type != new_column_type:
                        
                        query = "update " + table_name + " set " + column_name + " = replace(" + column_name + ", ' ', '');"
                        self.execute(query, silent)
                        
                        if new_column_type.find('date') == -1:
                            
                            query = "delete from " + table_name + " where " + column_name + " = 'Price';"
                            self.execute(query, silent)
                            query = "delete from " + table_name + " where " + column_name + " = '';"
                            self.execute(query, silent)
                            query = "alter table " + table_name + " alter column " + column_name + " type " + new_column_type\
                                     + " using " + column_name + "::" + new_column_type + ";"
                            self.execute(query, silent)
                            
                        else:
                            
                            query = "delete from " + table_name + " where " + column_name + " = '';"
                            self.execute(query)
                            query = "update " + table_name + " set " + column_name + " = to_date(" + column_name + ", 'DD.MM.YYYY');"
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
             
            msg = "ERROR (PSQLHandler.dropTablesByPattern): " + repr(e)
            logging.error(msg)
            print msg
         
        return
    
    
    def getConfidenceInterval(self, column_name, table_name, confidence_level = 5, silent = False):
        
        try:
            
            if not self.isColumnExistsInTable(column_name, table_name):
                return []
            
            query = "select " + column_name + " from " + table_name + ";"
            rows = self.execute(query, silent)
            rows =  np.asarray( [int(row[0]) for row in rows] )
            
            limits = np.percentile(rows, [confidence_level, 100 - confidence_level])
            
            return limits
             
        except Exception, e:
             
            msg = "ERROR (PSQLHandler.getConfidenceInterval): " + repr(e)
            logging.error(msg)
            print msg
         
        return
    
    
    def filterTableByIntervalFilter(self, table, result_table, filter_conditions, silent = False):
        
        try:
            
            query = "select * into " + result_table + " from " + table + " where "
            
            for i in range(len(filter_conditions)):
                
                cond = filter_conditions[i]
                
                column_name = cond[0]
                lower = cond[1][0]
                upper = cond[1][1]
            
                query = query + column_name + " > " + str(lower) + " and " + column_name + " < " + str(upper) + " "
                
            query = query + ";"
            print query
            
            self.execute(query, silent)
            
            return
             
        except Exception, e:
             
            msg = "ERROR (PSQLHandler.filterTableByIntervalFilter): " + repr(e)
            logging.error(msg)
            print msg
         
        return
    
# psql = PSQLHandler()



#  
# array = psql.getTableArrayByPattern("raw_.*")
# for table in array:
#     for item in psql.getTableColumnsList(table):
#         print item
# 
# psql.unionTables(array, "main")


# dir = "C:\\CIAN_DATA\\MSK\\SELL\\2015-03-09___00-39"
# files = ["RESULT_0.txt", "RESULT_1.txt", "RESULT_3.txt", "RESULT_4.txt", "RESULT_5.txt", "RESULT_6.txt"]
#  
# for f in files:
#      
#     result_file = os.path.join(dir, f)
#     dest_table = "raw_" + os.path.basename(dir).replace("-", "_") + "_" + f.split(".")[0]
#      
#     query = "ALTER TABLE " + dest_table + " DROP COLUMN areabedroom;"
#     psql.execute(query)

#     psql.loadCIANResultIntoPSQL(dest_table, result_file)
 
# array = psql.getTableArrayByPattern("raw_*")
# print array
#  
# for table in array:
#        
#     cols = ["floorstotal", "floor"]
#        
#     for col in cols:
#        
#         if psql.isColumnExistsInTable(col, table, silent = True):
#         
# #             query = "SELECT data_type, column_name FROM information_schema.columns where table_name = '" + table + "' and column_name = '" + col + "';"
# #             rows = psql.execute(query)
# #             
# #             print rows
# #             query = "UPDATE " + table + " SET " + col + " = replace(" + col + ", ' ', '');"
# #             rows = psql.execute(query)
#             query = "UPDATE " + table + " SET " + col + " = '-1' where " + col + " not similar to '%[0-9.\s]+%' ;" # = '.' or " + col + " = '';"
#             psql.execute(query)
#                 
#             query = "ALTER TABLE " + table + " ALTER COLUMN " + col + " TYPE bigint USING " + col + "::bigint;"
#             psql.execute(query)


# for table in array:
#       
#     if psql.isColumnExistsInTable("currentdate", table):
#         query = "ALTER TABLE " + table + " RENAME COLUMN currentdate TO date;"
#         psql.execute(query)
#     if psql.isColumnExistsInTable("postingdate", table):
#         query = "ALTER TABLE " + table + " DROP COLUMN postingdate;"
#         psql.execute(query)
#     if psql.isColumnExistsInTable("postingtime", table):
#         query = "ALTER TABLE " + table + " DROP COLUMN postingtime;"
#         psql.execute(query)
#     if psql.isColumnExistsInTable("currenttime", table):
#         query = "ALTER TABLE " + table + " DROP COLUMN currenttime;"
#         psql.execute(query)
#  
# columns = []
     
     
 
# result_columns_list = ["id", "link", "nrooms", "price", "pricem2", "currentdate"]
# 
# psql.dropTablesByPattern("^main*")
# psql.unionTables(array, "main", result_columns_list)
# 
# psql.getDeduplicatedTableSimple("main")
#   
# limits = psql.getConfidenceInterval("pricem2", "main", confidence_level = 10)
# filter_condition = [["pricem2", limits]]
# psql.filterTableByIntervalFilter("main", "main_conflim_pricem2", filter_condition)
# 
# 
# query = "drop table stats;"
# psql.execute(query)
# 
# query = "select nrooms, avg(pricem2), count(pricem2), currentdate as date into stats from \
#          main_conflim_pricem2 group by nrooms, currentdate order by nrooms, currentdate asc;"
#  
# psql.execute(query)
