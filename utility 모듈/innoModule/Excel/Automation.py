#-*- coding:utf-8 -*-

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
import os
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

if __name__ == "__main__" :
    import random 
    formula = [["=SUM(E2:E6)","=SUM(F2:F6)","=SUM(G2:G6)","=SUM(H2:H6)"]]
    data = []
    for i in range(5) :
        temp = []
        for j in range(4) :
            temp.append(random.randrange(1,10))
        data.append(temp)
    excel = ExcelAutomation(visible=True)
    excel.open("E:\\Downloads\\ChartExcel.xlsx")
    excel.setValue(("E2","H6"), data)
    excel.autoFit(("E2","H6"))
    excel.setValue(("E8","H8"), formula)
    excel.save("E:\\Downloads\\ChartExcel1.xlsx")
    excel.close()
        