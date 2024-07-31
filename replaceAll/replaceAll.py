import logging
import os
from typing import Annotated, Optional

import vtk

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode
from CondaSetUp import CondaSetUpCall,CondaSetUpCallWsl

import qt
import time
import platform
import threading
import subprocess
from functools import partial

#
# replaceAll
#


class replaceAll(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("replaceAll")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Tutorials")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#replaceAll">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""")

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#


def registerSampleData():
    """Add data sets to Sample Data module."""
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData

    iconsPath = os.path.join(os.path.dirname(__file__), "Resources/Icons")

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # replaceAll1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="replaceAll",
        sampleName="replaceAll1",
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, "replaceAll1.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames="replaceAll1.nrrd",
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums="SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        # This node name will be used when the data set is loaded
        nodeNames="replaceAll1",
    )

    # replaceAll2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category="replaceAll",
        sampleName="replaceAll2",
        thumbnailFileName=os.path.join(iconsPath, "replaceAll2.png"),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames="replaceAll2.nrrd",
        checksums="SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        # This node name will be used when the data set is loaded
        nodeNames="replaceAll2",
    )


#
# replaceAllParameterNode
#


@parameterNodeWrapper
class replaceAllParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """

    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# replaceAllWidget
#


class replaceAllWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)
        self.conda_wsl = CondaSetUpCallWsl()
        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/replaceAll.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = replaceAllLogic()

        # Connections
        self.ui.pushButton_searchFolder.connect("clicked(bool)", partial(self.openFinder,"input"))
        self.ui.pushButton_outputFolder.connect("clicked(bool)", partial(self.openFinder,"output"))
        self.ui.checkBox_overwrite.connect("clicked(bool)", self.overwrite)

        # Widgets visibility
        self.ui.label_time.setVisible(False)
        self.ui.progressBar.setVisible(False)
        self.ui.label_success.setVisible(False)
        self.ui.label_files.setVisible(False)

        # Progress bar
        self.time_log = 0
        self.log_path = os.path.join(slicer.util.tempDirectory(), "process.log")

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.applyButton.connect("clicked(bool)", self.onApplyButton)

        self.ui.applyButton.enabled = True

        # Make sure parameter node is initialized (needed for module reload)
        # self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """Ensure parameter node exists and observed."""
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        # self.setParameterNode(self.logic.getParameterNode())

        # # Select default input nodes if nothing is selected yet to save a few clicks for the user
        # if not self._parameterNode.inputVolume:
        #     firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
        #     if firstVolumeNode:
        #         self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[replaceAllParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        self._parameterNode = inputParameterNode
        if self._parameterNode:
            # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
            # ui element that needs connection.
            self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
            self._checkCanApply()

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
            self.ui.applyButton.toolTip = _("Compute output volume")
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = _("Select input and output volume nodes")
            self.ui.applyButton.enabled = False

    def _checkIO(self):
        warning_text = ""
        if not os.path.exists(self.ui.lineEdit_inputFolder.text) or (self.ui.lineEdit_inputFolder.text == ""):
            warning_text = warning_text + "Please enter a valid input path\n"
        
        if self.ui.lineEdit_outputFolder.text == "":
            warning_text = warning_text + "Please enter a valid output path\n"

        if self.ui.lineEdit_replaceByString.text == "":
            warning_text = warning_text + "Please enter the word to replace\n"

        if self.ui.lineEdit_replaceString.text == "":
            warning_text = warning_text + "Please enter the word to be replaced\n"

        if warning_text == "":
            return True
        
        else:
            qt.QMessageBox.warning(self.parent, "Warning", warning_text)
            return False

    def openFinder(self,nom : str,_) -> None :
        if nom == "input":
            folder = qt.QFileDialog.getExistingDirectory(self.parent, "Select the input folder")
            self.ui.lineEdit_inputFolder.setText(folder)
        elif nom == "output":
            folder = qt.QFileDialog.getExistingDirectory(self.parent, "Select the output folder")
            self.ui.lineEdit_outputFolder.setText(folder)

    def overwrite(self) -> None:
        if self.ui.checkBox_overwrite.isChecked():
            self.ui.lineEdit_outputFolder.setEnabled(False)
            self.ui.lineEdit_outputFolder.setText(self.ui.lineEdit_inputFolder.text)
            self.ui.pushButton_outputFolder.setEnabled(False)
        else:
            self.ui.lineEdit_outputFolder.setEnabled(True)
            self.ui.lineEdit_outputFolder.setText("")
            self.ui.pushButton_outputFolder.setEnabled(True)

    def onApplyButton(self):
        """Run processing when user clicks "Apply" button."""
        param = {}

        param["input_folder"] = self.ui.lineEdit_inputFolder.text
        param["replace"] = self.ui.lineEdit_replaceString.text
        param["by"] = self.ui.lineEdit_replaceByString.text
        param["output_folder"] = self.ui.lineEdit_outputFolder.text
        param["overwrite"] = self.ui.checkBox_overwrite.isChecked()
        param["log_path"] = self.log_path

        ready = True
        system = platform.system()
        if system == "Windows":
            self.ui.applyButton.setVisible(False)
            wsl = self.conda_wsl.testWslAvailable()
            if wsl : # check if wsl is available
                lib = self.check_lib_wsl()
                if not lib : # check if the lib required are installed
                    messageBox = qt.QMessageBox()
                    text = "Code can't be launch. \nWSL doen't have all the necessary libraries, please download the installer and follow the instructin here : https://github.com/DCBIA-OrthoLab/SlicerAutomatedDentalTools/releases/download/wsl2_windows/installer_wsl2.zip\nDownloading may be blocked by Chrome, this is normal, just authorize it."
                    ready = False
                    messageBox.information(None, "Information", text)
            else :
                messageBox = qt.QMessageBox()
                text = "Code can't be launch. \nWSL is not installed, please download the installer and follow the instructin here : https://github.com/DCBIA-OrthoLab/SlicerAutomatedDentalTools/releases/download/wsl2_windows/installer_wsl2.zip\nDownloading may be blocked by Chrome, this is normal, just authorize it."
                ready = False
                messageBox.information(None, "Information", text)
           
            if ready :
        
                if "Error" in self.conda_wsl.condaRunCommand([self.conda_wsl.getCondaExecutable(),"--version"]): # check if miniconda is install in wsl and is setup in SlicerConda
                    messageBox = qt.QMessageBox()
                    text = "Code can't be launch. \nConda is not setup in WSL. Please go the extension CondaSetUp in SlicerConda to do it."
                    ready = False
                    messageBox.information(None, "Information", text)

            if ready :
                # self.RunningUIWindows(True) 
                if not self.conda_wsl.condaTestEnv('replaceAll') : # check if the environnement exist
                    userResponse = slicer.util.confirmYesNoDisplay("The environnement to rename files doesn't exist, do you want to create it ? ", windowTitle="Env doesn't exist") # ask the persimission to create it
                    if userResponse : #create it in parallele to not blocking slicer
                    
                        process = threading.Thread(target=self.creation_env_wsl, args=())
                        process.start()
                        
                        start_time = time.time()
                        previous_time = start_time
                        current_time = start_time
                        
                        # self.ui.PredScanLabel.setText(f"The environnement doesn't exist, creation of the environnement")
                        # self.ui.TimerLabel.setText(f"time: : {current_time-start_time:.2f}s")

                        while process.is_alive():
                            slicer.app.processEvents()
                            current_time = time.time()
                            if current_time - previous_time > 0.3 :
                                previous_time = current_time
                                # self.ui.TimerLabel.setText(f"time: : {current_time-start_time:.2f}s")

                    else :
                        # self.ui.PredScanLabel.setText(f"The environnement doesn't exist, code can't be launch")
                        ready = False
                
                if ready : # if everything is setup, launch replaceAll_WSL in parallele on the environnement in wsl. Launch in parallele to not block slicer
                    process = threading.Thread(target=self.process_wsl, args=(param,))
                    process.start()
                    self.onProcessStarted()
                    
                    start_time = time.time()
                    previous_time = start_time
                    current_time = start_time
                    # self.ui.PredScanLabel.setText(f"Files in process")
                    # self.ui.TimerLabel.setText(f"time: {current_time-start_time:.2f}s")
                    while process.is_alive():
                        slicer.app.processEvents()
                        current_time = time.time()
                        if current_time - previous_time > 0.3 :
                            previous_time = current_time
                            # self.ui.TimerLabel.setText(f"time: {current_time-start_time:.2f}s")
                            # Progress bar display
                            if os.path.isfile(self.log_path):
                                time_progress = os.path.getmtime(self.log_path)
                                if time_progress != self.time_log and self.progress <= self.nbFiles:
                                    self.time_log = time_progress
                                    self.progress += 1
                                    progressbar_value = round((self.progress-1) / self.nbFiles * 100, 2)

                                    if progressbar_value < 100:
                                        self.ui.progressBar.setValue(progressbar_value)
                                        self.ui.progressBar.setFormat(str(progressbar_value) + "%")
                                    else:
                                        self.ui.progressBar.setValue(100)
                                        self.ui.progressBar.setFormat("100%")
                                    self.ui.label_files.setText("Number of processed files: " + str(self.progress - 1) + "/" + str(self.nbFiles))

                            # Time display
                            current_time = time.time() - self.universal_time
                            if current_time < 60:
                                timer = f"Time: {int(current_time)}s"
                            else:
                                timer = f"Time: {int(current_time/60)}min {int(current_time%60)}s"
                            self.ui.label_time.setText(timer)

                            # print(self.logic.cliNode.GetOutputText())
                    self.ui.label_success.setVisible(True)
                    self.ui.progressBar.setValue(100)
                    self.ui.progressBar.setFormat("100%")
                    self.ui.label_files.setText("Number of processed files: " + str(self.nbFiles) + "/" + str(self.nbFiles))

        else:
            if self._checkIO():
                # If additional output volume is selected then result with inverted threshold is written there
                # self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
                #                 self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)
                
                self.logic = replaceAllLogic(param,)
                self.logic.process()
                self.addObserver(self.logic.cliNode, vtk.vtkCommand.ModifiedEvent, self.onProcessUpdate)
                self.onProcessStarted()

    def condaCreateEnv(self,name,python_version,list_lib=[],tempo_file="tempo.txt",writeProgress=False):
        '''
        Creates a new Conda environment with the given name and Python version, and installs specified libraries.
        '''
        user = self.getUser()
        conda_path = self.getCondaExecutable()
        command_to_execute = ["wsl", "--user", user,"--","bash","-c", f"{conda_path} create -y -n {name} python={python_version} pip numpy-base"]
        if writeProgress : self.writeFile(tempo_file,"20")
        print("command to execute : ",command_to_execute)
        result = subprocess.run(command_to_execute, text=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE,env = slicer.util.startupEnvironment())
        if result.returncode==0:
            print("tt vas bien")
            self.condaInstallLibEnv(name,list_lib)
        else :
            print("error : ",result.stderr)

        if writeProgress : self.writeFile(tempo_file,"100")
        if writeProgress : self.writeFile(tempo_file,"end")

    def condaInstallLibEnv(self,name,requirements: list[str]):
        '''
        Installs a list of libraries in a specified Conda environment.
        '''
        print("requirements : ",requirements)
        path_activate = self.getActivateExecutable()
        path_conda = self.getCondaPath()
        user = self.getUser()
        if path_activate=="None":
                return "Path to conda no setup"
        else :
            if len(requirements)!=0 :

                command = f"source {path_activate} {name} && pip install"

                for lib in requirements :
                    command = command+ " "+lib
                command_to_execute = ["wsl", "--user", user,"--","bash","-c", command]
                print("command to execute in intsallLib wsl : ",command_to_execute)
                result = subprocess.run(command_to_execute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=slicer.util.startupEnvironment())
                if result.returncode==0:
                    print(f"Result : {result.stdout}")
                    return (f"Result : {result.stdout}")
                else :
                    print(f"Error : {result.stderr}")
                    return (f"Error : {result.stderr}")
            return "Nothing to install"

    def windows_to_linux_path(self,windows_path):
      '''
      convert a windows path to a wsl path
      '''
      windows_path = windows_path.strip()

      path = windows_path.replace('\\', '/')

      if ':' in path:
        drive, path_without_drive = path.split(':', 1)
        path = "/mnt/" + drive.lower() + path_without_drive

      return path

    def check_pythonpath_windows(self,name_env,file):
      conda_exe = self.conda_wsl.getCondaExecutable()
      command = [conda_exe, "run", "-n", name_env, "python" ,"-c", f"\"import {file} as check;import os; print(os.path.isfile(check.__file__))\""]
      print("command : ",command)
      result = self.conda_wsl.condaRunCommand(command)
      print("result = ",result)
      if "True" in result :
        return True
      return False

    def give_pythonpath_windows(self,name_env):
      paths = slicer.app.moduleManager().factoryManager().searchPaths
      mnt_paths = []
      for path in paths :
          mnt_paths.append(f"\"{self.windows_to_linux_path(path)}\"")
      pythonpath_arg = 'PYTHONPATH=' + ':'.join(mnt_paths)
      conda_exe = self.conda_wsl.getCondaExecutable()
      # print("Conda_exe : ",conda_exe)
      argument = [conda_exe, 'env', 'config', 'vars', 'set', '-n', name_env, pythonpath_arg]
      print("arguments : ",argument)
      self.conda_wsl.condaRunCommand(argument)

    def process_wsl(self,param):
      ''' 
      Function to launch replaceAll_wsl.
      Launch requirement.py in the environnement to be sure every librairy are well install with the good version
      Convert all the windows path to wsl path before launching the code
      '''
      name_env = "replaceAll"
      result_pythonpath = self.check_pythonpath_windows(name_env,"replaceAll_utils.replaceAll_WSL")
      if not result_pythonpath : 
        self.give_pythonpath_windows(name_env)
        result_pythonpath = self.check_pythonpath_windows(name_env,"replaceAll_utils.replaceAll_WSL")
      
      if result_pythonpath:
        param["input_folder"] = self.windows_to_linux_path(param["input_folder"])
        param["output_folder"] = self.windows_to_linux_path(param["output_folder"])
        param["log_path"] = self.windows_to_linux_path(param["log_path"])
        print("param : ",param)
        conda_exe = self.conda_wsl.getCondaExecutable()
        command = [conda_exe, "run", "-n", name_env, "python" ,"-m", f"replaceAll_utils.replaceAll_WSL"]
        for key,value in param.items() :
            command.append("\""+str(value)+"\"")
              
        print("command : ",command)

        result = self.conda_wsl.condaRunCommand(command)
        
        print("RESULT DE ALI IOS WSL : ",result)

    def creation_env_wsl(self):
      '''
      Create the environnement on wsl to run landmarks identification of ios files
      '''
      librairies = ["torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113",
                    "monai==0.7.0",
                    "--no-cache-dir torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0+cu113 --extra-index-url https://download.pytorch.org/whl/cu113",
                    "fvcore==0.1.5.post20220305",
                    "--no-index --no-cache-dir pytorch3d -f https://dl.fbaipublicfiles.com/pytorch3d/packaging/wheels/py39_cu113_pyt1110/download.html",
                    "rpyc",
                    "vtk",
                    "scipy"]
      
      name_env = "replaceAll"
      self.conda_wsl.condaCreateEnv(name_env,'3.9')
      result_pythonpath = self.check_pythonpath_windows(name_env,"replaceAll_utils.requirement")
      print("result_pythonpath : ",result_pythonpath)
      if not result_pythonpath : 
        self.give_pythonpath_windows(name_env)
        # result_pythonpath = self.check_pythonpath_windows(name_env,"replaceAll_utils.requirement") # THIS LINE IS WORKING
        result_pythonpath = self.check_pythonpath_windows(name_env,"replaceAll_utils.requirement")
        print("result_pythonpath : ",result_pythonpath)
        
      if result_pythonpath : 
        conda_exe = self.conda_wsl.getCondaExecutable()
        path_pip = self.conda_wsl.getCondaPath()+f"/envs/{name_env}/bin/pip"
        # command = [conda_exe, "run", "-n", name_env, "python" ,"-m", f"replaceAll_utils.requirement",path_pip] # THIS LINE IS WORKING
        command = [conda_exe, "run", "-n", name_env, "python" ,"-m", f"replaceAll_utils.requirement",path_pip]
        print("command : ",command)
        
        result = self.conda_wsl.condaRunCommand(command)
      
        print("RESULT OF REPLACEALL WSL REQUIREMENT : ",result)
        
        # for lib in librairies :
        #       self.conda_wsl.condaInstallLibEnv('replaceAll',[lib])

    def check_lib_wsl(self)->bool:
        '''
        Check if wsl contains the require librairies
        '''
        result1 = subprocess.run("wsl -- bash -c \"dpkg -l | grep libxrender1\"", capture_output=True, text=True)
        output1 = result1.stdout.encode('utf-16-le').decode('utf-8')
        clean_output1 = output1.replace('\x00', '')

        result2 = subprocess.run("wsl -- bash -c \"dpkg -l | grep libgl1-mesa-glx\"", capture_output=True, text=True)
        output2 = result2.stdout.encode('utf-16-le').decode('utf-8')
        clean_output2 = output2.replace('\x00', '')

        return "libxrender1" in clean_output1 and "libgl1-mesa-glx" in clean_output2

    def onProcessStarted(self):
        self.ui.label_time.setVisible(True)
        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setValue(0)
        self.universal_time = time.time()

        self.nbFiles = 0
        for _ in os.listdir(self.ui.lineEdit_inputFolder.text):
            self.nbFiles += 1

        self.progress = 0
        self.ui.label_files.setText("Number of processed files: " + str(self.progress) + "/" + str(self.nbFiles))
        self.ui.label_files.setVisible(True)

    def onProcessUpdate(self, caller, event):
        # Progress bar display
        if os.path.isfile(self.log_path):
            time_progress = os.path.getmtime(self.log_path)
            if time_progress != self.time_log and self.progress <= self.nbFiles:
                self.time_log = time_progress
                self.progress += 1
                progressbar_value = round((self.progress-1) / self.nbFiles * 100, 2)

                if progressbar_value < 100:
                    self.ui.progressBar.setValue(progressbar_value)
                    self.ui.progressBar.setFormat(str(progressbar_value) + "%")
                else:
                    self.ui.progressBar.setValue(100)
                    self.ui.progressBar.setFormat("100%")
                self.ui.label_files.setText("Number of processed files: " + str(self.progress - 1) + "/" + str(self.nbFiles))

        # Time display
        current_time = time.time() - self.universal_time
        if current_time < 60:
            timer = f"Time: {int(current_time)}s"
        else:
            timer = f"Time: {int(current_time/60)}min {int(current_time%60)}s"
        self.ui.label_time.setText(timer)
        if caller.GetStatus() & caller.Completed:
            print(self.logic.cliNode.GetOutputText())
            self.ui.label_success.setVisible(True)
            self.ui.progressBar.setValue(100)
            self.ui.progressBar.setFormat("100%")
            self.ui.label_files.setText("Number of processed files: " + str(self.nbFiles) + "/" + str(self.nbFiles))
            


#
# replaceAllLogic
#


class replaceAllLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self,input_folder=None,replace=None,by=None,output_folder=None,overwrite=None,log_path=None):
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)
        self.input_folder = input_folder
        self.replace = replace
        self.by = by
        self.output_folder = output_folder
        self.overwrite = overwrite
        self.log_path = log_path

        self.cliNode = None

    def process(self):
        parameters = {}

        parameters["input_folder"] = self.input_folder
        parameters["replace"] = self.replace
        parameters["by"] = self.by
        parameters["output_folder"] = self.output_folder
        parameters["overwrite"] = str(self.overwrite)
        parameters["log_path"] = self.log_path

        CLI_replaceAll = slicer.modules.replaceallcli
        self.cliNode = slicer.cli.run(CLI_replaceAll, None, parameters)

        return CLI_replaceAll


    # def process(self,
    #             inputVolume: vtkMRMLScalarVolumeNode,
    #             outputVolume: vtkMRMLScalarVolumeNode,
    #             imageThreshold: float,
    #             invert: bool = False,
    #             showResult: bool = True) -> None:
    #     """
    #     Run the processing algorithm.
    #     Can be used without GUI widget.
    #     :param inputVolume: volume to be thresholded
    #     :param outputVolume: thresholding result
    #     :param imageThreshold: values above/below this threshold will be set to 0
    #     :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
    #     :param showResult: show output volume in slice viewers
    #     """

    #     if not inputVolume or not outputVolume:
    #         raise ValueError("Input or output volume is invalid")

    #     import time

    #     startTime = time.time()
    #     logging.info("Processing started")

    #     # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    #     cliParams = {
    #         "InputVolume": inputVolume.GetID(),
    #         "OutputVolume": outputVolume.GetID(),
    #         "ThresholdValue": imageThreshold,
    #         "ThresholdType": "Above" if invert else "Below",
    #     }
    #     cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    #     # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    #     slicer.mrmlScene.RemoveNode(cliNode)

    #     stopTime = time.time()
    #     logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")


#
# replaceAllTest
#


class replaceAllTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_replaceAll1()

    def test_replaceAll1(self):
        """Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData

        registerSampleData()
        inputVolume = SampleData.downloadSample("replaceAll1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = replaceAllLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay("Test passed")
