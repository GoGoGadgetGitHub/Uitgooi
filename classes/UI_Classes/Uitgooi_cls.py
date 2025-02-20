from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow, QErrorMessage
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6 import QtGui
from UI import Ui_Uitgooi
from .Report_cls import Report
from shared.commen import *
from os import getcwd, walk, listdir, makedirs, sep
from os.path import basename, join, isfile, splitext, split, dirname, expanduser, isdir
from shared.paths import *
import csv
from shutil import copy
import json

class CopyFunction(QObject):
    finished = pyqtSignal()
    update_progress_bar = pyqtSignal()
    def __init__(self, UGInstance):
        super().__init__()
        self.UGInstance = UGInstance

    def run(self):
        for Class in self.UGInstance.orders:
            for ID in self.UGInstance.orders[Class]:
                for package in self.UGInstance.orders[Class][ID]:

                    #Grabbing the sorce path from the lookup table using the ID
                    srcPath = self.UGInstance.LookUp[ID]
                    file = basename(srcPath)
                    amount = self.UGInstance.orders[Class][ID][package]

                    self.UGInstance.copy_class_photo_if_needed(ID ,package, Class, amount)

                    try:
                        schemeKey = self.UGInstance.schemeLetter[package]
                    except KeyError:
                       self.UGInstance.errors.append(f'There is no package named {package} for order {ID}')
                       continue

                    schemeItem = self.UGInstance.scheme[schemeKey]

                    noSubFolders = not (self.has_sub_folder(schemeItem))
                    if noSubFolders:
                        for _ in range(amount):
                            self.UGInstance.copy_and_version(srcPath, path.join(self.UGInstance.dFolder, schemeKey, file))
                        continue

                    subFolders = list(schemeItem)
                    for folder in subFolders:
                        if folder != 'Z':
                            for _ in range(amount):
                                self.UGInstance.copy_and_version(srcPath, path.join(self.UGInstance.dFolder, schemeKey, folder, file))
        self.finished.emit()

    def has_sub_folder(self, schemeItem):
        if type(schemeItem) is str:
            return False

        if len(list(schemeItem)) == 1:
            return not(list(schemeItem)[0] == 'Z')

        return True


class Uitgooi(Ui_Uitgooi, QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Uitgooi")
        self.progress.setValue(0)
        self.sFolder = ''
        self.dFolder = ''
        self.kFolder = ''
        self.LookUp = {}
        self.orders = {}
        self.schemes = {}
        self.scheme = {}
        self.schemeLetter = {}
        self.OkIDs = {}
        self.packagesOrdered = {}
        self.packagesCopied = {}
        self.packagesThatNeedK = []
        self.errors = []
        self.NoIDOrder = 0
        self.progressInicrement = 0

        self.thrd = QThread()
        self.worker = CopyFunction(self)
        self.worker.moveToThread(self.thrd)
        self.thrd.started.connect(self.worker.run)
        self.worker.finished.connect(self.thrd.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.update_progress_bar.connect(self.update_progress_bar)
        self.thrd.finished.connect(self.thrd.deleteLater)

        self.read_schemes()
        self.populate_combobox()
        self.cmbScheme.setCurrentText("2025")

        self.btnSelectSFolder.clicked.connect(self.select_s_folder_clicked)
        self.btnSelectDFolder.clicked.connect(self.select_d_folder_clicked)
        self.btnSelectKFolder.clicked.connect(self.select_k_folder_clicked)
        self.btnBegin.clicked.connect(self.begin_clicked)

        self.btnSelectDFolder.setDisabled(True)
        self.btnSelectKFolder.setDisabled(True)
        self.btnBegin.setDisabled(True)     
        
  #------------------------------UITGOOI LOGIC------------------------------  
  
    def calculate_total_opperations(self):
        copies = 0
        for package in self.packagesOrdered:
            try:
                schemeKey = self.schemeLetter[package]
            except KeyError:
                continue

            schemeItem = self.scheme[schemeKey]
            amount = self.packagesOrdered[package]

            #case of no subfolders
            if type(schemeItem) is str:
                copies += amount
                continue
            
            #case of one subfoler
            if len(schemeItem) == 1:
                #case of one sub folder being class pictures
                try:
                    schemeItem['Z']
                    copies += 2 * amount
                #case of one sub folder not being class pictures
                except KeyError:
                    copies += amount                
                continue

            #case of multiple sub folders
            copies += len(schemeItem) * amount
        return copies

    def update_progress_bar(self):
        self.progress.setValue(self.progress.value() + 1)

    def scheme_letters(self):
        """
        Goes over the scheme dictionary wich has the package name and the print size in one, and extracts the package name (i.e. A, B, C etc.)
        Then it saves then in a dictionary like this:
            'A' : 'A-8x5'
        This just saves time when trying to match an order in the csv to the right file it needs to be coppied too
        """
        for key in self.scheme:
            self.schemeLetter[key[0]] = key

    def set_default(self):
        """
        Sets combobox selection to default scheme
        """
        #NOTE: these constants need to be worked on first
        with open(path.join(SCHEMES, "default.txt"), 'r') as dflt:
            content = dflt.read()
            print(content)
            self.cmbScheme.setCurrentText(content)

    def populate_combobox(self):
        self.cmbScheme.clear()
        self.cmbScheme.addItems([i for i in self.schemes])

    def read_schemes(self):
        """
        Loads all saved schemes into class from schemes.txt
        """
        with open(path.join(SCHEMES, "schemes.json"), 'r') as json_file:
            self.schemes = json.load(json_file)

    def create_dict(self, folder):
        """
        Creates dict with the following format:
            {'image name':'image path'}
        
        This helps with constant lookup time

        folder: str object that is the path of the folder to be added to the lookup dictionary
        """
        #TODO: This might be wrong ngl
        strangeFilenameList = []
        for r,d,fs in walk(folder):
            for f in fs:
                try:
                    key = f.split('.')[0].split('-')[1]
                except IndexError:
                    strangeFilenameList.append(f)
                    continue

                self.LookUp[key] = join(r,f)
        fileNames = '<br/>' + '<br/>'.join(strangeFilenameList)
        message = f"The following files have names which the program cannot process: {fileNames}"
        if len(strangeFilenameList) > 0:
            QErrorMessage(self).showMessage(message)



    def get_selection(self):
        """
        Determines weather to use a selected scheme or the default scheme
        """
        selection = self.cmbScheme.currentText()
        self.scheme = self.schemes[selection]

    def print_progress(self, path):
        print("Copying: " + path)

    def copy_class_photo_if_needed(self, ID, package, Class, amount):
        """
        Copies class photo if needed to Klas-Foto folder
        """
        if package[0] in self.packagesThatNeedK:
            try:
                ClassPPath = self.LookUp[Class]
            except KeyError:
                self.errors.append(f"{Class} could not be found in the class photo folder! - {ID}")
                return
            file = basename(ClassPPath)
            for _ in range(amount):
                self.copy_and_version(ClassPPath, path.join(self.dFolder,'Klas-Fotos',file))

    def copy_and_version(self, source, destination):
        """
        Checks wether a file exits and if it does it implements a file versionion function, else it just makes the
        required directory and copies the file to it.
        """
        if isfile(destination):
            name, extension = splitext(destination)
            #This is the versioning part, it cheacks for an availble file name starting form    file (2).etx
            for i in range(1000):
                i += 2
                new_file = f'{name} ({i}){extension}'
                if not isfile(new_file):
                    #Once it finds one it does the copy with the new file name and breaks the loop, then exits scope
                    self.print_progress(basename(destination))
                    self.worker.update_progress_bar.emit()
                    copy(source, new_file)
                    break
        else:
            self.print_progress(basename(destination))
            makedirs(split(destination)[0], exist_ok= True)
            self.worker.update_progress_bar.emit()
            copy(source, destination)

    def extract_class_p(self):
        """
        Checking Scheme to determain which packages need class pictures
        """
        for i in self.scheme:
            if self.scheme[i] != 'E':
                for j in self.scheme[i]:
                    if j == 'Z':
                        self.packagesThatNeedK.append(i[0])

    def count_orders(self, ID, package):
        #litteraly just counting the number of orders of each kind
        if package in self.packagesThatNeedK:
            try:
                self.packagesOrdered["KF"] += 1
            except KeyError:
                self.packagesOrdered["KF"] = 1

        try:
            self.packagesOrdered[package] += 1
        except KeyError:
            self.packagesOrdered[package] = 1

    def print_order(self):
        order = ""
        for Class in self.orders:
            order += f"{Class}:\n"
            for ID in self.orders[Class]:
                order += f"\t{ID}:\n"
                for package in self.orders[Class][ID]:
                    order += f"\t\t{package}: {self.orders[Class][ID][package]}\n"

        return order

    def IDok (self, ID, package):
        #This seems to basiclly be looking for duplicate orders
        #It keeps a list of orders that have been added, and if it encounters the same order more then once
        #It asks the user if this is ok?

        #NOTE: It's just never being called
        orderExists = ID in self.OkIDs and self.OkIDs[ID] == package;

        if orderExists:
            ok = show_dialog_y_n("Attention!", f"{ID} {package} has been found more then once. Is this correct?")

            if not ok:
                show_dialog_ok("Attention!", "Please fix the shpreadsheet and try again.")
                exit(0)

            self.OkIDs[order[0]] = order[1]
            return

    def read_csv_order_form(self):  
        """
        Reads the order csv and populates an dictionary associated with the order
        """
        csvFile = ''
        index = 0
        dirs = listdir(self.dFolder)
        #Find the csv file
        while '.csv' not in csvFile:
            csvFile = dirs[index]
            index += 1
        with open(self.dFolder + '/' + csvFile, encoding='utf-8-sig') as csv_file:
            #Determain delimiter
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(list(csv_file)[0])
            csv_file.seek(0)
            delim = dialect.delimiter

            csv_reader = csv.reader(csv_file, delimiter = delim)

            NonExistantID = {}
            rows = list(csv_reader)
            for row in rows:
                ID = row[0]
                package = row[1]
                if ID == '':
                    show_dialog_ok("Attention!", "There was an order with no ID!")
                    self.NoIDOrder += 1
                    continue

                #This checks for a ID that does not exist, in other words an ID on the CSV that has no file in the ORG folder
                if ID not in self.LookUp:
                    NonExistantID[ID] = None
                    continue

                #Looking for dupicate order
                self.IDok(ID, package)

                Class = self.LookUp[ID].split(sep)[-2]

                if Class not in self.orders:
                    self.count_orders(ID, package)
                    self.orders[Class] = {ID:{package:1}}

                elif ID not in self.orders[Class]:
                    self.count_orders(ID, package)
                    self.orders[Class][ID] = {package:1} 

                elif package not in self.orders[Class][ID]:
                    self.count_orders(ID, package)
                    self.orders[Class][ID][package] = 1

                else:
                    self.count_orders(ID, package)
                    self.orders[Class][ID][package] += 1

        self.errors.append(f"There were/was {self.NoIDOrder} order(s) with no ID!")
        return NonExistantID

    def present_in_diffrent_class(self, cls, ID):
        """
        Tests to see if a photo is present in multiple classes
        """
        for Class in self.orders:
            if ID in self.orders[Class] and cls != Class:
                return True
        return False

    def count_copied(self):
        """
        Counts the amount of files copied
        """
        self.packagesCopied = {key:0 for key in self.packagesOrdered}

        for package in self.packagesCopied:
            try:
                packFullName = self.schemeLetter[package]
            except KeyError:
               continue

            packPath = path.join(self.dFolder, packFullName)
            firstSub = listdir(packPath)[0]
            firstSubPath = path.join(self.dFolder, packFullName, firstSub)

            if isdir(firstSubPath):
                self.packagesCopied[package] = len(listdir(firstSubPath))
            else:
                self.packagesCopied[package] = len(listdir(packPath))

        try:
            self.packagesCopied["KF"] = len(listdir(path.join(self.dFolder, "Klas-Fotos")))
        except (FileExistsError, FileNotFoundError):
            pass

    #------------------------------UI IMPLEMENTATON------------------------------
    #TODO: A better way of handeling default file dialog path would be saving and reading the last path used
    def reset(self):
        """
        Resets the UI
        """
        self.imgPreview.setPixmap(QtGui.QPixmap())
        self.lblDestination.setText("Destination:")
        self.lblKlasfotos.setText("")
        self.lblSource.setText("School: ")
        self.progress.setValue(0)
        self.sFolder = ''
        self.dFolder = ''
        self.kFolder = ''
        self.LookUp = {}
        self.orders = {}
        self.OkIDs = {}
        self.packagesOrdered = {}
        self.packagesCopied = {}
        self.packagesThatNeedK = []
        self.errors = []
        self.NoIDOrder = 0
        self.progressInicrement = 0

        self.thrd = QThread()
        self.worker = CopyFunction(self)
        self.worker.moveToThread(self.thrd)
        self.thrd.started.connect(self.worker.run)
        self.worker.finished.connect(self.thrd.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.update_progress_bar.connect(self.update_progress_bar)
        self.thrd.finished.connect(self.thrd.deleteLater)

        self.btnSelectDFolder.setEnabled(False)
        self.btnSelectKFolder.setEnabled(False)
        self.btnBegin.setEnabled(False)
    
    def select_d_folder_clicked(self):
        """
        Retrieves the path of the destination folder from windows file dialog.
        This is where the file structure will be created and the images will be copied to.

        Also calls the read_csv_order_form method
        """
        found = False
        self.dFolder = QFileDialog.getExistingDirectory(self, 'Select a destination path')
        if self.dFolder == '':
            return
        else:
            try:
                for item in listdir(self.dFolder):
                    if '.csv' in item:
                        found = True
                if found == True:
                    self.lblDestination.setText("Destination: " + self.dFolder.split("/")[-1])
                    self.btnSelectKFolder.setDisabled(False)
                else:
                    print("Error", "Can't find .csv file in destinaion folder.")
                    return
            except FileNotFoundError:
                show_dialog_ok("Error", "File not found!")

    def select_s_folder_clicked(self):
        """
        Gets the path of the source folder from windows file dialog.
        This is the folder from which the images will be copied
        """
        self.LookUp = {}
        self.sFolder = QFileDialog.getExistingDirectory(self, 'Select a source path')
        if self.sFolder == '':
            return
        elif "raam" not in self.sFolder.lower():
            show_dialog_ok("Error", "Make sure you selected the raam folder")
            return
        school = self.sFolder.split("/")[-2]
        self.lblSource.setText("School: " + school)
        self.create_dict(self.sFolder)
        preview = self.LookUp[next(iter(self.LookUp))]
        self.show_preview(preview)
        self.btnSelectDFolder.setDisabled(False)

    def select_k_folder_clicked(self):
        """
        Gets the path where the class photos are saved from windows file dialog and ads them to the lookup dictionary
        """
        school = self.sFolder.split('/')[-2]
        self.kFolder = QFileDialog.getExistingDirectory(self, 'Choose Class Photo Folder', dirname(self.sFolder))
        folderSelected = self.kFolder[self.kFolder.index(school):]
        self.lblKlasfotos.setText(folderSelected)
        if self.kFolder == '':
            return
        """
        Adding class photos and their paths to the look up dictionary
        """
        for r,d,fs in walk(self.kFolder):
            for f in fs:
                self.LookUp[f[:f.rfind('.')]] = join(r,f)

        self.btnBegin.setDisabled(False)
    
    def begin_clicked(self):
        """
        Checks to see what scheme is selected and calls the appropriate methods
        """
        #show_console()
        self.get_selection()
        self.scheme_letters()
        self.extract_class_p()
        nonExistantID =  self.read_csv_order_form()
        if len(nonExistantID) > 0:
            IDs = '\n' + '\n'.join(nonExistantID)
            show_dialog_ok("Error", f"There were {len(nonExistantID)} photo numbers on the order form that cannot be found in the RAAM folder {IDs}")
            exit(0)
        total = self.calculate_total_opperations()
        print(total)
        self.progress.setMaximum(total)
        # MultiThreading
        self.thrd.start()
        #EndMultiThreading
        self.worker.finished.connect(self.begin_clicked_continue)

    def begin_clicked_continue(self):
        self.count_copied()
        #hide_console()
        self.report = Report(parent=self)
        self.report.show()

    def show_preview(self, image):
        """
        Shows the first image in the folder as a preview

        image: str object that is a path to an image
        """
        self.imgPreview.setPixmap(QtGui.QPixmap(image))
        self.imgPreview.setScaledContents(True)
        self.imgPreview.setMaximumWidth(230)
        self.imgPreview.setMaximumHeight(400)
