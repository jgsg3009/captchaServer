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
