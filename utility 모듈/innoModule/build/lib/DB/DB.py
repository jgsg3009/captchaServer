#-*- coding:utf-8 -*-
from java.lang import Class
from java.sql import DriverManager
from java.sql import Types

from itertools import izip_longest
import traceback

class DB():
    def __init__(self, driver_name = "oracle", host="localhost", port = None, service_name = "orclcdb.localdomain"):
        self.conn = None
        self.jdbc_url = None
        self.port = None
        self.stmt = None
        self.pstmts = []
        self.pstmtQuerys = []
        self.cstmts = []
        self.cstmtStates = []
        self.resultSet = None
        self.resultSetMetaData = None
        self.columnCount = None
        try :
            if driver_name == 'oracle' :
                Class.forName("oracle.jdbc.driver.OracleDriver")
                jdbc_header = "jdbc:oracle:thin"
                if port == None :
                    port = "1521" 
                self.jdbc_url = "{}:@{}:{}/{}".format(jdbc_header,host,port,service_name)
            elif driver_name == 'oracle_sid' :
                Class.forName("oracle.jdbc.driver.OracleDriver")
                jdbc_header = "jdbc:oracle:thin"
                if port == None :
                    port = "1521" 
                self.jdbc_url = "{}:@{}:{}:{}".format(jdbc_header,host,port,service_name)                
            elif driver_name == 'sql_server' :
                Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver")
                jdbc_header = "jdbc:sqlserver"
                if port == None :
                    port = "1433"
                self.jdbc_url ="{}://{}:{};DatabaseName={}".format(jdbc_header,host,port,service_name)
        except :
            traceback.print_exc()
            print("please check driver name")
    def connect(self, username, password) :
        try :
            self.conn = DriverManager.getConnection(self.jdbc_url, username, password)
            self.stmt = self.conn.createStatement()
        except :
            traceback.print_exc()
            if not self.conn == None :
                self.conn.close()
    def close(self):
        try :
            if not self.stmt == None :
                self.stmt.close()
            if not len(self.pstmts) == 0 :
                for pstmt in self.pstmts :
                    pstmt.close()
            if not self.resultSet == None :
                self.resultSet.close()
            if not len(self.cstmts) == 0 :
                for cstmt in self.cstmts :
                    cstmt.close()
        finally :
            if not self.conn == None :
                self.conn.close()
    def executeQuery(self, query, values = None):
        try :
            if values == None :
                if not self.resultSet == None :
                    self.resultSet.close()
                self.resultSet = self.stmt.executeQuery(query)
            else :
                if not self.resultSet == None :
                    self.resultSet.close()
                pstmt = self.checkQueryDup(query)
                for index, value in enumerate(values) :
                    pstmt.setString(index+1,value)
                self.resultSet = pstmt.executeQuery()
            self.resultSetMetaData = self.resultSet.getMetaData()
            self.columnCount = self.resultSetMetaData.getColumnCount()
        except :
            traceback.print_exc()
            print("executeQuery failed")
    def executeUpdate(self, query, values = None):
        try :
            if values == None :
                affectedRowNum = self.stmt.executeUpdate(query)
            else :
                pstmt = self.checkQueryDup(query)
                for index, value in enumerate(values) :
                    pstmt.setString(index+1,value)
                affectedRowNum = pstmt.executeUpdate()
            return affectedRowNum
        except :
            traceback.print_exc()
            print("executeUpdate failed")

    def transaction(self, queryList, valueList = []) :
        try :
            self.conn.setAutoCommit(False) 
            transaction_set = enumerate(izip_longest(queryList,valueList, fillvalue=None))
            for repeat,(query,values) in transaction_set:
                # stop transaction if query is None
                if query == None :
                    break
                else :
                    if values == None :
                        self.stmt.executeUpdate(query)
                    else :
                        pstmt = self.checkQueryDup(query)
                        for index,value in enumerate(values) :
                            pstmt.setString(index+1,value)
                        pstmt.executeUpdate()
        except :
            traceback.print_exc()
            self.conn.rollback()
            print("transaction failed in ({}/{})".format(repeat, len(queryList)))
        finally:
            self.conn.setAutoCommit(True)
    def callproc(self, procedure_name, values = []):
        cstmt = self.checkProcedureDup(procedure_name,len(values))
        for index,value in enumerate(values) :
            cstmt.setString(index+1,value)
        cstmt.execute()
    def fetchone(self):
        if not self.resultSet == None :
            if self.resultSet.next() :
                return self.fetchoneRow()
        
    def fetchall(self):
        result = []
        if not self.resultSet == None :
            while self.resultSet.next() :
                result.append(self.fetchoneRow())
        return result
    
    def fetchmany(self, count=1):
        result = []
        repeat = 0
        while self.resultSet.next() and repeat < count :
            result.append(self.fetchoneRow())
            repeat += 1
        return result
    def rownumber(self):
        if not self.resultSet == None :
            return self.resultSet.getRow()
    def checkQueryDup(self, query):
        for index, pstmtQuery in enumerate(self.pstmtQuerys) :
            if query == pstmtQuery :
                return self.pstmts[index] 
        pstmt = self.conn.prepareStatement(query)
        self.pstmts.append(pstmt)
        self.pstmtQuerys.append(query)
        return pstmt
    def checkProcedureDup(self, procedure_name, procedure_valueNum):
        for index, (name,valueNum) in enumerate(self.cstmtStates) :
            if procedure_name == name and procedure_valueNum == valueNum:
                return self.cstmts[index]
        question_marks = ",".join(["?" for _ in range(procedure_valueNum)])
        query = "{"+"call {}({})".format(procedure_name,question_marks)+"}"
        cstmt = self.conn.prepareCall(query)
        self.cstmts.append(cstmt)
        self.cstmtStates.append((procedure_name, procedure_valueNum))
        return cstmt
    def fetchoneRow(self):
        if not self.resultSet == None :
            rowValues = []
            for index in range(1,self.columnCount+1) :
                columnType = self.resultSetMetaData.getColumnType(index)
                if columnType in [ Types.NUMERIC,
                                   Types.REAL, 
                                   Types.FLOAT, 
                                   Types.DOUBLE ] :
                    s = self.resultSet.getString(index);
                    s = float(s)
                elif columnType in [ Types.TINYINT,
                                     Types.SMALLINT, 
                                     Types.INTEGER, 
                                     Types.BIGINT, 
                                     Types.DECIMAL ] :
                    s = self.resultSet.getString(index);
                    s = int(s)
                elif columnType in [ Types.BOOLEAN, Types.BIT ] :
                    s = self.resultSet.getString(index);
                    s = bool(s)
                else :
                    s = self.resultSet.getString(index)
                rowValues.append(s)
            return rowValues
