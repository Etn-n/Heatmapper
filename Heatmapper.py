import subprocess
import os
import sys
import csv
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox, QTabWidget, QCheckBox, QTableWidget,QDialogButtonBox, QTableWidgetItem, QApplication, QLineEdit, QWidget, QLabel, QGridLayout, QGroupBox, QPushButton, QFileDialog
from PySide6.QtGui import QIcon, QColor
from pandas import read_csv
import matplotlib.pyplot as plt

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(1000,800)
        self.setWindowTitle("Heatmapper")
        self.setWindowIcon(QIcon(f"{os.path.dirname(os.path.realpath(__file__))}/data/icon.png"))
        Big_layout = QGridLayout()
        self.setLayout(Big_layout)
        self.fileselectWidget = QGroupBox("Select the Directory to search or File to analyse")
        self.fileselectlayout = QGridLayout()
        ##Dir Path Text Box + Options
        self.lineedit= QLineEdit()
        self.lineedit.setPlaceholderText("Select a Directory")
        self.lineedit.returnPressed.connect(self.GetItems)
        

        self.BtnBox = QDialogButtonBox(orientation=Qt.Horizontal,centerButtons=True)
        self.OldBtn = QCheckBox(tristate=True,text="Get all files")
        self.OldBtn.clicked.connect(self.changeOldBtn)

        self.BtnBox.addButton(self.OldBtn,QDialogButtonBox.YesRole)

        ##CSV File Select
        self.fileLineedit= QLineEdit()
        self.fileLineedit.setPlaceholderText("Select a CSV File")
        self.fileLineedit.returnPressed.connect(self.GetItems)

        
        self.dirselect = QPushButton("Select Directory")
        self.dirselect.setFocusPolicy(Qt.NoFocus)
        self.dirselect.setDefault(True)
        self.dirselect.clicked.connect(self.open_file_dialog_Dossier)
        self.fileselect = QPushButton("Select a CSV File")
        self.fileselect.setFocusPolicy(Qt.NoFocus)
        self.fileselect.setDefault(True)
        self.fileselect.clicked.connect(self.open_file_dialog_File)
        self.CSVBtn = QPushButton("View CSV")
        self.CSVBtn.setFocusPolicy(Qt.NoFocus)
        self.CSVBtn.setDefault(True)
        self.CSVBtn.clicked.connect(self.makeTab)
        self.RunBtn = QPushButton("Run Search")
        self.RunBtn.setFocusPolicy(Qt.NoFocus)
        self.RunBtn.setDefault(True)
        self.RunBtn.clicked.connect(self.GetItems)
        self.Run3dBtn = QPushButton("Run 3d Plot")
        self.Run3dBtn.setFocusPolicy(Qt.NoFocus)
        self.Run3dBtn.setDefault(True)
        self.Run3dBtn.clicked.connect(self.plot3d)
        self.Run3dBtn.setDisabled(1)
        self.RunAnalysisBtn = QPushButton("Run Heatmap")
        self.RunAnalysisBtn.setFocusPolicy(Qt.NoFocus)
        self.RunAnalysisBtn.setDefault(True)
        self.RunAnalysisBtn.clicked.connect(self.makeHeatmapTab)
        self.RunAnalysisBtn.setDisabled(1)
        self.DupeBtn = QPushButton("Run Dupe Detection")
        self.DupeBtn.setFocusPolicy(Qt.NoFocus)
        self.DupeBtn.setDefault(True)
        self.DupeBtn.clicked.connect(self.makeDupeTab)
        self.DupeBtn.setDisabled(1)
        self.RunBtn.setDisabled(1)
        self.fileselectlayout.addWidget(self.lineedit,0,0,1,1)
        self.fileselectlayout.addWidget(self.BtnBox,1,0,Qt.AlignmentFlag.AlignHCenter)
        self.fileselectlayout.addWidget(self.fileLineedit,2,0,1,1)
        self.fileselectlayout.addWidget(self.dirselect,0,1)
        self.fileselectlayout.addWidget(self.CSVBtn,2,2)
        self.fileselectlayout.addWidget(self.fileselect,2,1)
        self.fileselectlayout.addWidget(self.RunBtn,0,2)
        
        self.fileselectWidget.setLayout(self.fileselectlayout)
        self.CSVselectedLabel= QLineEdit(text="CSV File currently in use : none",readOnly=True,alignment=Qt.AlignmentFlag.AlignCenter,frame=False)
        self.CSVselectedLabel.setStyleSheet('color : lime;padding:2px;background-color:rgba(0,0,0,0)')
        self.fileselectlayout.addWidget(self.CSVselectedLabel,3,0,1,3)
        Big_layout.addWidget(self.fileselectWidget,0,0,1,5)


        

        self.profMaxSpinBox = QSpinBox(minimum=0)
        self.profMaxSpinBox.setDisabled(1)
        self.profMaxSpinBox.setToolTip("Select the depth at which to look for")
        self.TabBox = QTabWidget()
        self.TabBox.setDisabled(1)
        self.OutputTab = QTableWidget()
        
        
        self.Depthlabel=QLabel(text="Select Depth to analyse :")
        self.Depthlabel.setStyleSheet('color : lime;padding:2px;background-color:rgba(0,0,0,0)')
        Big_layout.addWidget(self.Depthlabel,1,0)
        Big_layout.addWidget(self.profMaxSpinBox,1,1)
        Big_layout.addWidget(self.RunAnalysisBtn,1,2)
        Big_layout.addWidget(self.DupeBtn,1,3)
        Big_layout.addWidget(self.Run3dBtn,1,4)
        Big_layout.addWidget(self.TabBox,2,0,1,5)



    def makeDupeTab(self):
        if os.path.exists(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempdupesorted.csv"):
            os.remove(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempdupesorted.csv")
        rowIndex=0
        df = read_csv(self.selectCSV,index_col=False)
        df = df[df.duplicated(['Name','Size'], keep=False)]
        df = df.drop(df.columns[1:-3],axis=1)
        Hash_index = df.columns.get_loc("Name")
        df.to_csv(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempdupe.csv", index=False)
        subprocess.run(["powershell","-Command",f"{os.path.dirname(os.path.realpath(__file__))}/data/xan.exe sort -s {Hash_index} -o '{os.path.dirname(os.path.realpath(__file__))}/data/tempdupesorted.csv' '{os.path.dirname(os.path.realpath(__file__))}/data/tempdupe.csv'"])
        os.remove(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempdupe.csv")
        csvDupe = f'{os.path.dirname(os.path.realpath(__file__))}/data/tempdupesorted.csv'

        for i in range(self.TabBox.count()):
            if self.TabBox.tabText(i)== "Duplicates":
                self.TabBox.removeTab(i)

        with open(csvDupe ,encoding='utf-8',newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            headers = next(csv_reader)
            lines = sum(1 for line in csvfile)
        self.DupeTable= QTableWidget(columnCount=4,rowCount=lines)
        self.DupeTable.cellClicked.connect(self.cellClickDupe)
        self.DupeTable.setHorizontalHeaderLabels(headers)
        with open(csvDupe ,encoding='utf-8',newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            next(csv_reader, None)
            for row in csv_reader:
                for i in range(0,4):
                    item = QTableWidgetItem(f"{row[i]}")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.DupeTable.setItem(rowIndex,i,item)
                rowIndex+=1
        self.DupeTable.resizeColumnsToContents()
        self.TabBox.addTab(self.DupeTable, "Duplicates")
    def makeCSVTab(self):
        rowIndex=0
        with open(self.selectCSV ,encoding='utf-8',newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            self.headers = next(csv_reader)
        TableLayout= QTableWidget(columnCount=self.colNum+1,rowCount=self.lines)
        TableLayout.setHorizontalHeaderLabels(self.headers)
        
        for i in range(0,self.colNum+1):
            with open(self.selectCSV ,encoding='utf-8',newline='') as csvfile:
                csv_reader = csv.reader(csvfile, delimiter=',')
                rowIndex=0
                next(csv_reader, None)
                for row in csv_reader:
                    item = QTableWidgetItem(f"{row[i]}")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    TableLayout.setItem(rowIndex,i,item)
                    rowIndex+=1
        TableLayout.resizeColumnsToContents()
        return TableLayout
    def plot3d(self):
        df = read_csv(self.selectCSV)
        x = f"{self.profMaxSpinBox.value()}"
        Lvl='path'+x
        size_per_folder_per_year = df.groupby([Lvl,'timestamp'], as_index=False)['Size'].sum()
        #print(size_per_folder_per_year[Lvl].count())
        x,y,z,dx,dy,dz = [],[],[],[],[],[]

        X = size_per_folder_per_year[Lvl].to_numpy()
        Y = size_per_folder_per_year['timestamp'].to_numpy()
        Z = size_per_folder_per_year['Size'].to_numpy()
        dates = list(range(Y.min(),Y.max()+2))
        #print(size_per_folder_per_year)
        lastpath,xvalue = "",0
        indexX,labels=[],[]
        for i in range(0,len(size_per_folder_per_year)):
            if X[i] == lastpath:
                indexX.append(xvalue)
            else :
                lastpath = X[i]
                xvalue+=1
                labels.append(lastpath+'    ')
                indexX.append(xvalue)

        labels.append("")

        #print(len(indexX))

        for i in range(0,len(size_per_folder_per_year)):
            x.append(indexX[i]-0.875),y.append(Y[i]+0.125),z.append(0),dx.append(0.75),dy.append(0.75),dz.append((Z[i]))

        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        ax.bar3d(x, y, z, dx, dy, dz)

        plt.xticks(ticks=list(range(0,len(labels))),labels=labels,rotation=0, ha='right', rotation_mode='anchor')
        plt.yticks(dates,rotation=45, ha='right', rotation_mode='anchor')
        plt.show()
    def makeHeatmapTab(self):
        if os.path.exists(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempsort.csv"):
            os.remove(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempsort.csv")
        for i in range(self.TabBox.count()):
            if self.TabBox.tabText(i)== "Heatmap":
                self.TabBox.removeTab(i)

        x = self.profMaxSpinBox.value()+1
        subprocess.run(["powershell","-Command",f"{os.path.dirname(os.path.realpath(__file__))}/data/xan.exe sort -s {x} -o '{os.path.dirname(os.path.realpath(__file__))}/data/tempsort.csv' '{self.selectCSV}'"])
        self.sortedCSV = f"{os.path.dirname(os.path.realpath(__file__))}/data/tempsort.csv"
        with open(self.sortedCSV, newline='',encoding='utf-8') as csvfile:
            next(csvfile)
            self.fullweight = sum(int(r[-1]) for r in csv.reader(csvfile))
        #print(self.fullweight)
        self.BigList = {}
        self.name=""
        self.annee = 0
        self.mass=0
        with open(self.sortedCSV, newline='',encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            next(csv_reader, None)
            for row in csv_reader:
                if row[x] == self.name and row[0] == self.annee :
                    self.mass += int(row[-1])
                if row[x] == self.name and row[0] != self.annee :
                    self.BigList[self.name].append((self.annee,self.mass))
                    self.mass,self.annee =int(row[-1]),row[0]
                if row[x] != self.name :
                    if self.name != "" :
                        self.BigList[self.name].append((self.annee,self.mass))
                    self.mass,self.annee = int(row[-1]),row[0]
                    self.name = row[x]
                    self.BigList[self.name] = []
            self.BigList[self.name].append((self.annee,self.mass))
        os.remove(f"{os.path.dirname(os.path.realpath(__file__))}/data/tempsort.csv")

        rec = read_csv(self.selectCSV)
        uniqueTime = (rec['timestamp'].unique()).tolist()
        HMHeaders= ['Path']
        vertLab=[]
        keys=list(self.BigList.keys())
        for i in uniqueTime:
            HMHeaders.append(str(i))
        for i in range(len(keys)):
            vertLab.append("")
        self.HeatmapTable= QTableWidget(columnCount=len(uniqueTime)+1,rowCount=len(keys))
        self.HeatmapTable.cellClicked.connect(self.cellClick)
        self.HeatmapTable.setHorizontalHeaderLabels(HMHeaders)
        self.HeatmapTable.setVerticalHeaderLabels(vertLab)
        HMHeaders.remove('Path')
        
        for i in range(len(keys)):
            item = QTableWidgetItem(keys[i])
            item.setTextAlignment(Qt.AlignCenter)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.HeatmapTable.setItem(i,0,item)
        rowIndex,colIndex = 0,1
        for j in self.BigList:
            for i in HMHeaders :
                if [item for item in self.BigList[j] if item[0] == i] != [] :
                    value='{:05.2f}'.format([item for item in self.BigList[j] if item[0] == i][0][1]/(1024**3))
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    item.setBackground(QColor(160,160,160))                
                    if [item for item in self.BigList[j] if item[0] == i][0][1] > 0.01*self.fullweight :
                        item.setBackground(QColor(92,196,180))
                    if [item for item in self.BigList[j] if item[0] == i][0][1] > 0.03*self.fullweight :
                        item.setBackground(QColor(196,186,0))
                    if [item for item in self.BigList[j] if item[0] == i][0][1] > 0.05*self.fullweight :
                        item.setBackground(QColor(247,164,22))
                    if [item for item in self.BigList[j] if item[0] == i][0][1] > 0.07*self.fullweight :
                        item.setBackground(QColor(255,0,0))
                    self.HeatmapTable.setItem(rowIndex,colIndex,item)
                else :
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    
                    self.HeatmapTable.setItem(rowIndex,colIndex,item)
                colIndex+=1
            colIndex=1
            rowIndex+=1
        self.HeatmapTable.resizeColumnsToContents()
        self.TabBox.addTab(self.HeatmapTable, "Heatmap")
    def cellClickDupe(self,row,column):
        link = self.DupeTable.item(row,1).text().replace("/","\\")+"\\"+self.DupeTable.item(row,2).text()
        print(link)
        subprocess.Popen(fr'explorer /select,"{link}"')
    def cellClick(self,row,column):
        link = self.HeatmapTable.item(row,0).text().replace("/","\\")
        print(link)
        os.startfile(fr"{link}")
    def changeOldBtn(self):
        if self.OldBtn.checkState() == Qt.Unchecked:
            self.OldBtn.setText("Get all files")
        if self.OldBtn.checkState() == Qt.PartiallyChecked:
            self.OldBtn.setText("Get only files over 5 years old")
        if self.OldBtn.checkState() == Qt.Checked:
            self.OldBtn.setText("Get only files over 10 years old")
    def GetItems(self):
        commandList = ["powershell",
            "-NoProfile", 
            "-ExecutionPolicy", "Bypass", 
            "-File", f"{os.path.dirname(os.path.realpath(__file__))}/data/GetAllItems.ps1",
            "-fichier", f'{self.folderpath}',
            "-pathOutput", f"{os.path.dirname(os.path.realpath(__file__))}/data"]

        if self.OldBtn.checkState() == Qt.PartiallyChecked:
            commandList.append("-plus5ans")
        if self.OldBtn.checkState() == Qt.Checked:
            commandList.append("-plus10ans")     

        subprocess.run(commandList)
        self.selectCSV = f"{os.path.dirname(os.path.realpath(__file__))}/data/output.csv"
        self.lineedit.setText(f"")
        self.updateLabel()
        self.Run3dBtn.setDisabled(0)
        self.RunAnalysisBtn.setDisabled(0)
        self.DupeBtn.setDisabled(0)
    def makeTab(self):
        self.CSVTable = self.makeCSVTab()
        for i in range(self.TabBox.count()):
            if self.TabBox.tabText(i)== "CSV":
                self.TabBox.removeTab(i)
        self.TabBox.addTab(self.CSVTable, "CSV")
    def updateLabel(self):
        self.CSVselectedLabel.setText(f"CSV File currently in use : {self.selectCSV}")
        with open(self.selectCSV, newline='',encoding='utf-8') as csvfile:
            self.colNum = csvfile.readline().count(',')
            self.lines = sum(1 for line in csvfile)
            #print("colonnes:",self.colNum," path depth :",self.colNum-4)
            #print("lignes:",self.lines)
        self.profMaxSpinBox.setDisabled(0)
        self.profMaxSpinBox.setValue(0)
        self.TabBox.setDisabled(0)
        self.profMaxSpinBox.setMaximum(self.colNum-4)
    def open_file_dialog_Dossier(self):
        dialog = QFileDialog(self,"Choose a Folder")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setNameFilter("")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            self.folderpath = dialog.selectedFiles()[0]
            self.lineedit.setText(f"{self.folderpath}")
            print(self.folderpath)
            self.RunBtn.setDisabled(0)
    def open_file_dialog_File(self):
        dialog = QFileDialog(self,"Choose a Folder")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("CSV File (*.csv)")
        dialog.setViewMode(QFileDialog.ViewMode.List)
        if dialog.exec():
            self.selectCSV = dialog.selectedFiles()[0]
            self.fileLineedit.setText("")
            self.updateLabel()
            print(self.selectCSV)
            self.Run3dBtn.setDisabled(0)
            self.RunAnalysisBtn.setDisabled(0)
            self.DupeBtn.setDisabled(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MainWindow()
    widget.show()

    sys.exit(app.exec())