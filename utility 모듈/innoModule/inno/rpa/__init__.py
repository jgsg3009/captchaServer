#-*- coding:utf-8 -*-

# common Module
import os
from jaydebeapi import _jython_set_classpath
from glob import glob

currentPath = os.path.dirname(__file__)

jars = glob(currentPath+'/jdbc_drivers/*') + glob(currentPath+'/jna/*') + glob(currentPath+'/poi-4.1.2/*') + glob(currentPath+'/poi-4.1.2/*/*')
jars = map(lambda x : unicode(x),jars)

for jar in jars :
    _jython_set_classpath([jar])


#-*- coding:utf-8 -*-

from java.io import FileInputStream
from java.io import FileOutputStream
from org.apache.poi.xssf.usermodel import XSSFWorkbook
from org.apache.poi.hssf.usermodel import HSSFWorkbook
from org.apache.poi.ss.util import CellReference

class Excel() :

    def __init__(self) :
        self.workBook = None
        self.workBookType = None
        self.filename = None
        self.inputStream = None
        self.outputStream = None
        self.lastSheet = None
        self.lastSheetIndentifier = None
        self.sheets = {}
        
    def open(self,filename = "") :
        # check filename is string
        if not isinstance(filename,str) :
            print("filename type must be str.")
            return None
        
        self.inputStream = FileInputStream(filename)
        self.filename = filename
                     
        if filename == "" :
            self.workBook = XSSFWorkbook()
            self.workBookType = "xlsx"
        elif filename[-5:] == ".xlsx" :
            self.workBook = XSSFWorkbook(self.inputStream)
            self.workBookType = ".xlsx"
        elif filename[-4:] == ".xls" :
            self.workBook = HSSFWorkbook(self.inputStream)
            self.workBookType = ".xls"
        else :
            print("inVaild File format.")           
         
    def save(self, filename = ""):
        
        if not isinstance(filename,str) :
            print("filename type must be str.")
            return None
        
        if filename == "" :
            filename = self.filename
            
        self.outputStream = FileOutputStream(filename) 
        self.workBook.write(self.outputStream)
        
    def close(self) :
        if not self.workBook == None :
            self.workBook.close()
        if not self.inputStream == None :
            self.inputStream.close()  
        if not self.outputStream == None :
            self.outputStream.close()
                     
    def getCell(self, cellAddress, sheet = 0) :
        
        sheet, rowIndex, colIndex = self._manageCellIndex(cellAddress,sheet)
            
        row = sheet.getRow(rowIndex)
        if row == None :
            return ""
        
        cell = row.getCell(colIndex)
        if cell == None : 
            return ""
        
        return cell.getStringCellValue()
        
    def setCell(self,cellAddress,content,sheet = 0):
        
        sheet, rowIndex, colIndex = self._manageCellIndex(cellAddress,sheet)
            
        row = sheet.getRow(rowIndex)
        if row == None :
            row = sheet.createRow(rowIndex)
            
        cell = row.getCell(colIndex)
        if cell == None : 
            cell = row.createCell(colIndex)
            
        cell.setCellValue(content)
         
    def deleteCell(self,cellAddress, sheet = 0):
        
        sheet, rowIndex, colIndex = self._manageCellIndex(cellAddress,sheet)
            
        row = sheet.getRow(rowIndex)
        if row == None :
            return None
        
        row.removeCell(row.getCell(colIndex))
        
    def _manageCellIndex(self,cellAddress,sheet):
                
        if self.lastSheetIndentifier == sheet :
            sheet = self.lastSheet
        else :
            self.lastSheetIndentifier = sheet
            if isinstance(sheet,str) :
                sheet = self.workBook.getSheet(sheet)
            else :
                sheet = self.workBook.getSheetAt(sheet)              
            self.lastSheet = sheet
        
        if isinstance(cellAddress,str) :
            cr = CellReference(cellAddress)
            rowIndex = cr.getRow()
            colIndex = cr.getCol()
        else : 
            rowIndex, colIndex = cellAddress
            
        return sheet, rowIndex, colIndex

from java.lang import System

OS = System.getProperty("os.name").lower()

if OS.find("windows") != -1 :
    # java jna class
    from com.sun.jna import Pointer
    from com.sun.jna.platform.win32.COM.util.office.excel import ComExcel_Application
    from com.sun.jna.platform.win32.COM.util.office.excel import ComIApplication
    from com.sun.jna.platform.win32.COM.util import Factory
    from com.sun.jna.platform.win32 import OaIdl
    from com.sun.jna.platform.win32 import Variant
    from com.sun.jna.platform.win32 import Ole32

    from com.sun.jna.platform.win32 import WTypes
    # java basic class
    from java.io import File as javaFile
    # python module
    #import os
    import traceback
    import tempfile

    class ExcelAutomation():
        def __init__(self, visible=True, autoClose=True, forceSave=True):
            Ole32.INSTANCE.CoInitializeEx(Pointer.NULL, Ole32.COINIT_MULTITHREADED)
            self.fact = Factory()
            self.excel = self.fact.createObject(ComExcel_Application)
            self.excelApp = self.excel.queryInterface(ComIApplication)
            self.excelApp.setVisible(visible)
            self.autoClose = autoClose
            self.forceSave = forceSave
            self.originalExist = None
            # from com.sun.jna.platform.win.32.WinDef.LCID;
            # you can set your locale by this.
            #fact.setLCID(LCID(0x0412)); KR
            #fact.setLCID(LCID(0x0409)); US        
        
        def open(self, filename=None):
            if filename :
                self.wb = self.excelApp.getWorkbooks().Open(filename)
                self.originalExist = True
            else :
                self.wb = self.excelApp.getWorkbooks().Add();
                self.originalExist = False
        # range example: (1,1) or "A1" or ((1,1),(5,5)) or ("A1","E5") 
        def setValue(self, cellRange, data):
            cellRange = self._manageRangeIndex(cellRange)
            excelArray = self._excel2DArray(data)
            dataHolder = Variant.VARIANT()
            dataHolder.setValue(Variant.VT_ARRAY + Variant.VT_VARIANT, excelArray)
            if isinstance(cellRange, tuple) :
                self.wb.getActiveSheet().getRange(*cellRange).setValue(dataHolder)
            else :
                self.wb.getActiveSheet().getRange(cellRange).setValue(dataHolder)
            excelArray.destroy()
            
        def autoFit(self, cellRange):
            cellRange = self._manageRangeIndex(cellRange)
            if isinstance(cellRange, tuple) :
                self.wb.getActiveSheet().getRange(*cellRange).getEntireColumn().AutoFit()
            else :
                self.wb.getActiveSheet().getRange(cellRange).getEntireColumn().AutoFit()
            
        def save(self, path=None):
            try :
                if self.wb : 
                    # save anoterfile
                    if path :  
                        if self.forceSave : 
                            directory = os.path.dirname(path)
                            filename = path.replace(directory,'')
                            createdFile = javaFile(directory,filename)
                            createdFile.delete()
                        self.wb.SaveAs(path)
                    # save file withCreated
                    else :
                        if self.originalExist :
                            self.wb.Save()
                        else : 
                            self.wb.SaveAs(tempfile.gettempdir()+"undefined.xlsx")
                else :
                    raise Exception("workbook not exist")
            except :
                traceback.print_exc()
                raise Exception("save file failed")
            
        def close(self):
            if not self.excelApp == None :
                self.excelApp.getActiveWorkbook().Close(False)
                self.excelApp.Quit()
            self.fact.disposeAll()
            Ole32.INSTANCE.CoUninitialize()

        def _excel2DArray(self, data):
            # when primitive
            if not isinstance(data,list) :            
                data = [[data]]
            else :
                # when data is 1DArray
                if not isinstance(data[0],list) :
                    data = [data]
            rowSize = len(data[0])
            colSize = len(data)
            wrapped = OaIdl.SAFEARRAY.createSafeArray(rowSize, colSize)
            var = Variant.VARIANT()
            for i in range(colSize) :
                for j in range(rowSize) :
                    var.setValue(Variant.VT_BSTR, WTypes.BSTR(str(data[i][j])))
                    wrapped.putElement(var, j, i)
            return wrapped
        
        def _manageRangeIndex(self, cellRange):
            if isinstance(cellRange,tuple) :
                #(tuple,tuple)
                if isinstance(cellRange[0],tuple) :
                    cellRange = list(cellRange)
                    for index, cellAddress in enumerate(cellRange) :
                        cellRange[index] = self._manageCellIndex(cellAddress)
                    cellRange = tuple(cellRange)
                else : 
                    #(str,str)
                    if isinstance(cellRange[0],str) :
                        pass
                    #tuple
                    else :
                        cellRange = self._manageCellIndex(cellRange)
            # 단일 셀 값
            else :
                cellRange = self._manageCellIndex(cellRange)

            return cellRange
        
        def _manageCellIndex(self, cellAddress):
            if isinstance(cellAddress,tuple) :
                row = str(cellAddress[0])
                col = self._indexToLetter(cellAddress[1])
                cellAddress = col+row
            elif isinstance(cellAddress,str) :
                pass
            else :
                raise Exception("Only str and tuple can be cellAddress")
            
            return cellAddress
        def _indexToLetter(self, n):
            letter = ""
            while n > 0:
                n, r = divmod(n - 1, 26)
                letter = chr(65 + r) + letter
            return letter

#import os
import jaydebeapi as jdb
import traceback
from itertools import izip_longest

class DBClient() :
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

