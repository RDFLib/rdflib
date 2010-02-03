# -*- coding: utf-8 -*-


class CSVWriter(object):
    
    def __init__(self):
        self.f = None
        self.Columns = None

    def Open(self,columns, filename):
        self.Columns = columns
        self.f = open(filename,'a')
        # header
        if self.Columns != None:
            for k in self.Columns:
                self.f.write(k + '\t')
            self.f.write('\n')
            self.f.flush()
    
    def WriteLine(self,line):
        self.f.write(line + '\n')
        self.f.flush()
    
    def WriteListEntry(self,list):
        for k in list:
            if k != None:
                val = str(k).replace('\n',' ').replace('\t', ' ')
            else:
                val = ''
            self.f.write(val + '\t')
        self.f.write('\n')
        self.f.flush()       
    
    def Write(self,list):
        # write data rows
        for d in list:
            self.WriteEntry(d)
    
    def WriteEntry(self,d):
        for k in self.Columns:
            if d.has_key(k):
                val = str(d[k]).replace('\n',' ').replace('\t', ' ')
            else:
                val = ''
            self.f.write(val + '\t')
        self.f.write('\n')
        self.f.flush()
     
    
    def Close(self):        
        self.f.close()
        self.f = None
        
def WriteAllResults(filename, columns, list):
    w = CSVWriter()
    w.Open(columns, filename)    
    w.Write(list)            
    w.Close()
