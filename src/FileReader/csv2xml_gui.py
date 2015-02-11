import csv, os, sys, io
from Tkinter import *
from tkFileDialog import askopenfilename
# from sim_error import MyError
import StringIO

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

csvFilenames = []
company = ['First', 'Second', 'Third']
state = False

class ProcessCSV(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        formRow = ''
        requestRow = ''
        parent.wm_title("convert csv to xml")
        self.makeForm(parent)
        self.makeRequest(parent)        

    def fileDialog(self, entry):
        print(entry)
        filename = askopenfilename()
        csvFilenames.append(filename)
        entry.insert(0, filename)
        entry.pack()
        print(csvFilenames)
    
    def onClick(self):
        global state
        state = not state
    
    def makeForm(self, parent):
        for i in range(5):
            formRow = Frame(parent)        
            entry = Entry(formRow)
            button = Button(formRow, text='select a file', command=(lambda entry=entry:self.fileDialog(entry)))
            
            # print('entry is {}'.format(entry))
            print('entry is ', entry)
                                
            formRow.pack(side=TOP, fill=X, padx=5, pady=5)
            button.pack(side=LEFT)
            entry.pack(side=RIGHT, expand=YES, fill=X)

    def makeRequest(self, parent):
        requestRow = Frame(parent)
        cancel = Button(requestRow, text='cancel')
        submit = Button(requestRow, text='Summit', padx=10, pady=10, command=(lambda:csv2xml()))
        checkButton = Checkbutton(requestRow, text="Export to same file ?",command=(lambda:self.onClick()))
        requestRow.pack(side=TOP, fill=X, padx=5, pady=5)
        cancel.pack(side=LEFT)
        checkButton.pack(side=RIGHT)
        submit.pack(side=RIGHT)

def csv2xml():
    desFile = ''
    for srcFile in csvFilenames:
        basename = os.path.basename(srcFile)
        print(basename)
        # check which company provide the src files. 
        for item in company:
            if item in basename:
                sender = item
                break            
        filename, fileExt = os.path.splitext(srcFile)
    
        # consolidating the outfile to one file, the provider should be the same.
        if state:
            if desFile:
                if item not in desFile:
                    print('error')
                    # raise MyError("File should be from the same company")
            else:
                desFile = os.path.dirname(srcFile) + '/' + item + '.xml'
        else:
            desFile = filename + '.xml'

        
        xmlData = open(desFile, 'w')
        buf = StringIO.StringIO()
        buf.write('<?xml version="1.0"?>' + "\n")
        buf.write('<root>' + "\n")
        buf.write('  <data sender="' + sender + '">\n')

        rowNum = 0
        with open(srcFile, 'r') as csvFile:
            print('srcFile', srcFile)
            print('in file reading')
            csvData = csv.reader(csvFile)
            for row in csvData:
                print(row)
                eleNum = len(row)
                if rowNum == 0:
                    date = row[0]
                elif rowNum > 1: 
                    write_temp = '    <value date="'+date+'" '+'time="'+row[0]+'" '+'type="float">'+row[1]+'</value>\n'
                    buf.write(write_temp)
                    #buf.write('    <value date="{}" time="{}" type="float">{}</value>\n'.format(date, row[0], row[1]))
                rowNum += 1
            buf.write('  </data>' + "\n")
            buf.write('</root>')
        print(buf.getvalue())
        xmlData.write(buf.getvalue())
        buf.close()
        xmlData.close()
            
if __name__=='__main__':
    root = Tk()
    temp = ProcessCSV(root)
    root.mainloop()
