#-*- coding:utf-8 -*-

import os
import jaydebeapi as jdb
import traceback
from itertools import izip_longest

class DB() :
    def __init__(self, driver_name = "oracle", host="localhost", port = None, service_name = "orclcdb.localdomain"):
        self.conn = None
        self.cur = None
        self.driver = None
        self.jdbc_url = None
        self.jdbc_jar_path = None
        self.port = None
        self.exceptionClose = False
        
        currentPath = os.path.dirname(__file__)
        try :
            if driver_name == 'oracle' :
                self.driver = "oracle.jdbc.driver.OracleDriver"
                jdbc_header = "jdbc:oracle:thin"
                if port == None :
                    port = "1521" 
                self.jdbc_url = "{}:@{}:{}/{}".format(jdbc_header,host,port,service_name)
                self.jdbc_jar_path = "{}/jdbc_drivers/ojdbc8-19.3.0.0.jar".format(currentPath)
            elif driver_name == 'oracle_sid' :
                self.driver = "oracle.jdbc.driver.OracleDriver"
                jdbc_header = "jdbc:oracle:thin"
                if port == None :
                    port = "1521" 
                self.jdbc_url = "{}:@{}:{}:{}".format(jdbc_header,host,port,service_name)
                self.jdbc_jar_path = "{}/jdbc_drivers/ojdbc8-19.3.0.0.jar".format(currentPath)                
            elif driver_name == 'sql_server' :
                self.driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
                jdbc_header = "jdbc:sqlserver"
                if port == None :
                    port = "1433"
                self.jdbc_url ="{}://{}:{};DatabaseName={}".format(jdbc_header,host,port,service_name)
                self.jdbc_jar_path = "{}/jdbc_drivers/mssql-jdbc-8.2.2.jre8.jar".format(currentPath)
        except :
            traceback.print_exc()
            raise Exception("import module failed")
        
    def connect(self, username, password) :
        try :
            self.conn = jdb.connect(self.driver,self.jdbc_url, [username, password], self.jdbc_jar_path)
        except :
            traceback.print_exc()
            raise Exception("DB connection error")

    def close(self):
        try :
            if not self.cur == None :
                self.cur.close()
        finally :
            if not self.conn == None :
                self.conn.close()
    def execute(self, query, values = None):
        try :
            if self.cur == None :
                self.cur = self.conn.cursor()
                
            if values == None :
                self.cur.execute(query)
            else :
                self.cur.execute(query,values)
        except :
            traceback.print_exc()
            if self.exceptionClose :
                self.conn.close()
            raise ExecuteException(query,values)

    def executemany(self, query, valueList = []):
        try :
            if self.cur == None :
                self.cur = self.conn.cursor()
                
            self.cur.executemany(query,valueList)
        except :
            traceback.print_exc()
            if self.exceptionClose :
                self.conn.close()
            raise ExecuteException(query)

    def transaction(self, queryList, valueList = []) :
        try :
            self.conn.jconn.setAutoCommit(False) 
            transaction_set = enumerate(izip_longest(queryList,valueList, fillvalue=None))
            for step,(query,values) in transaction_set:
                # stop transaction if query is None
                if query == None :
                    break
                else :
                    if values == None :
                        self.execute(query)
                    else :
                        self.execute(query,values)
            self.conn.commit()
        except :
            traceback.print_exc()
            self.conn.jconn.rollback()
            if self.exceptionClose :
                self.close()
            raise TransactionException(step, len(queryList))
        finally:
            if not self.conn.jconn == None :
                self.conn.jconn.setAutoCommit(True)
                
    def callproc(self, procedure_name, values = None):
        try : 
            if values == None :
                len_values = 0
            else :
                len_values = len(values)
            question_marks = ",".join(["?" for _ in range(len_values)])
            query = "{"+"call {}({})".format(procedure_name,question_marks)+"}"
            self.execute(query,values)
        except :
            traceback.print_exc()
            if self.exceptionClose :
                self.close()
            raise ProcException()
        
    def fetchone(self):
        if not self.cur == None :
            if not self.cur._rs == None :
                return self.cur.fetchone()
            else :
                raise NonResultSetException()
        else : 
            raise NonCursorException()
        
    def fetchall(self):
        if not self.cur == None :
            if not self.cur._rs == None :
                return self.cur.fetchall()
            else :
                raise NonResultSetException()
        else : 
            raise NonCursorException()
        
    def fetchmany(self, num = 1):
        if not self.cur == None :
            if not self.cur._rs == None :
                return self.cur.fetchmany(num)
            else :
                raise NonResultSetException()
        else :
            raise NonCursorException()
        
    def affectedRow(self):
        if not self.cur == None :
                return self.cur.rowcount
        else :
            raise NonCursorException()
            
    class NonCursorException(Exception) :
        def __init__(self, msg = None):
            if msg == None :
                self.msg = "execute first before call fetch"
            else : 
                self.msg = msg
        def __str__(self):
            return self.msg
        
    class NonResultSetException(Exception):
        def __init__(self,msg = None):
            if msg == None :
                self.msg = "fetch failed. resultSet doesn't exist."
            else : 
                self.msg = msg
        def __str__(self) :
            return self.msg   

    class ExecuteException(Exception):
        def __init__(self, query, values):
            if values == None :
                self.msg = "execute failed in query : {}".format(query)
            else : 
                self.msg = "execute failed in query : {}, values : {}".format(query, values)
        def __str__(self) :
            return self.msg    
        
    class ProcException(Exception) :
        def __init__(self, msg = None):
            if msg == None :
                self.msg = "callproc failed."
            else : 
                self.msg = msg  
        def __str__(self) :
            return self.msg    
        
    class TransactionException(Exception):         
        def __init__(self, step, len_queryList):
            self.msg = "transaction failed in ({}/{})".format(step, len_queryList)
        def __str__(self) :
            return self.msg
