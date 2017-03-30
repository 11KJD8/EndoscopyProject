import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy

#
# EndoscopyProject
#

class EndoscopyProject(ScriptedLoadableModule):
  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Endoscopy Project"
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["Kyle Delaney"]
    self.parent.helpText = """
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Kyle Delaney.
    """

#
# EndoscopyProjectWidget
#

class EndoscopyProjectWidget(ScriptedLoadableModuleWidget):
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    #self.inputSelector = slicer.qMRMLNodeComboBox()
    #self.inputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    #self.inputSelector.selectNodeUponCreation = True
    #self.inputSelector.addEnabled = False
    #self.inputSelector.removeEnabled = False
    #self.inputSelector.noneEnabled = False
    #self.inputSelector.showHidden = False
    #self.inputSelector.showChildNodeTypes = False
    #self.inputSelector.setMRMLScene( slicer.mrmlScene )
    #self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    #parametersFormLayout.addRow("Input Volume: ", self.inputSelector)

    #
    # output volume selector
    #
    #self.outputSelector = slicer.qMRMLNodeComboBox()
    #self.outputSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
    #self.outputSelector.selectNodeUponCreation = True
    #self.outputSelector.addEnabled = True
    #self.outputSelector.removeEnabled = True
    #self.outputSelector.noneEnabled = True
    #self.outputSelector.showHidden = False
    #self.outputSelector.showChildNodeTypes = False
    #self.outputSelector.setMRMLScene( slicer.mrmlScene )
    #self.outputSelector.setToolTip( "Pick the output to the algorithm." )
    #parametersFormLayout.addRow("Output Volume: ", self.outputSelector)

    #
    # threshold value
    #
    #self.imageThresholdSliderWidget = ctk.ctkSliderWidget()
    #self.imageThresholdSliderWidget.singleStep = 0.1
    #self.imageThresholdSliderWidget.minimum = -100
    #self.imageThresholdSliderWidget.maximum = 100
    #self.imageThresholdSliderWidget.value = 0.5
    #self.imageThresholdSliderWidget.setToolTip("Set threshold value for computing the output image. Voxels that have intensities lower than this value will set to zero.")
    #parametersFormLayout.addRow("Image threshold", self.imageThresholdSliderWidget)

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    #self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    #self.enableScreenshotsFlagCheckBox.checked = 0
    #self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    #parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Selector
    #
    self.catheterSelector = slicer.qMRMLNodeComboBox()
    self.catheterSelector.nodeTypes = ["vtkMRMLTransformNode"]
    self.catheterSelector.setMRMLScene( slicer.mrmlScene )
    parametersFormLayout.addRow("Catheter Transform: ", self.catheterSelector)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.catheterSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.catheterSelector.currentNode()
  
  def onApplyButton(self):
    logic = EndoscopyProjectLogic()
    catheterToRasNode = self.catheterSelector.currentNode()
    if catheterToRasNode == None:
      print('Failed to Apply')
      return
    catheterToRasNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, self.onTransformModified)
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    #logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), imageThreshold, enableScreenshotsFlag)

  def onTransformModified(self,caller,event):
    import numpy as np
    catheterToRasNode = self.catheterSelector.currentNode()
    catheterToRasTransform = vtk.vtkGeneralTransform()
    catheterToRasNode.GetTransformToWorld(catheterToRasTransform)
    catheterPosition_Catheter = np.array([0.0, 0.0, 0.0])
    catheterPosition_Ras = catheterToRasTransform.TransformFloatPoint(catheterPosition_Catheter)
    slicer.mrmlScene.RemoveNode(catheterPosition_Ras)
    ArteryFids = slicer.util.getNode('Artery')
    #N = ArteryFids.GetNumberOfFiducials()
    #fiducialPositions = np.zeros((N,3))
    #fiducialPositions = np.zeros([N,3])
    #p = np.array([0,0,0])
    #for i in range(N):
      #Fiducials should already be RAS looking at Markups module
      #ArteryFids.GetNthFiducialPosition(i,p)
      #fiducialPositions[i] = p
    pathPoint_Ras = [0,0,0]
    self.closestPointFiducials(ArteryFids,catheterPosition_Ras,pathPoint_Ras)
    #print(catheterPosition_Ras)
    x = pathPoint_Ras[0] - catheterPosition_Ras[0]
    y = pathPoint_Ras[1] - catheterPosition_Ras[1]
    z = pathPoint_Ras[2] - catheterPosition_Ras[2]
    catheterToCenterTransform =  vtk.vtkMatrix4x4()
    catheterToCenterTransform.SetElement(0,3,x)
    catheterToCenterTransform.SetElement(1,3,y)
    catheterToCenterTransform.SetElement(2,3,z)
    catheterToCenterTransform.SetElement(0,0,1)
    catheterToCenterTransform.SetElement(1,1,1)
    catheterToCenterTransform.SetElement(2,2,1)
    catheterToCenterTransform.SetElement(3,3,1)


    adjustedCatheterPosition_Ras = slicer.vtkMRMLLinearTransformNode()
    adjustedCatheterPosition_Ras.ApplyTransformMatrix(catheterToCenterTransform)
    slicer.mrmlScene.AddNode(adjustedCatheterPosition_Ras)
    #catheterToRasNode.ApplyTransformMatrix(transformationMatrix)
    return

  def closestPointFiducials(self, pathFids_Ras, camPosition_Ras, pathPoint_Ras):
    n = pathFids_Ras.GetNumberOfFiducials()
    if n < 2:
      return False
    minDistance = 9000000
    for i in range(n - 1):
      l1 = [0, 0, 0]
      l2 = [0, 0, 0]
      pathFids_Ras.GetNthFiducialPosition(i, l1)
      pathFids_Ras.GetNthFiducialPosition(i + 1, l2)
      t = vtk.mutable(0)
      cp = [0, 0, 0]
      d = vtk.vtkLine.DistanceToLine(camPosition_Ras, l1, l2, t, cp)
      if d < minDistance:
        minDistance = d
        for j in range(3):
          pathPoint_Ras[j] = cp[j]
    return True

  def centerCatheter(self,catheterPosition,fiducialPositions,N):
    #First tries and finds the closest fiducial point
    pointB = fiducialPositions[0]
    #print(pointB)
    shortestDistance = numpy.linalg.norm(catheterPosition - fiducialPositions[0])
    for point in range(1,N):
      distance = numpy.linalg.norm(catheterPosition - fiducialPositions[point])
      if distance < shortestDistance:
        pointB = fiducialPositions[point] #This will be the second point of the line the catheter will snap to
        shortestDistance = distance
    if numpy.array_equal(pointB,fiducialPositions[0]):
      pointA = fiducialPositions[0]
      pointB = fiducialPositions[1]
    else:
      pointA = fiducialPositions[point-1]
    self.pointLineDistance(pointA,pointB,catheterPosition)
    return

  def pointLineDistance(self,pointA,pointB,pointP):
    u = pointB - pointA
    print(u)
    #v = pointP - pointA
    
    
#
# EndoscopyProjectLogic
#

class EndoscopyProjectLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('EndoscopyProjectTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class EndoscopyProjectTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    #self.setUp()
    self.test_EndoscopyProject1()

  def test_EndoscopyProject1(self):
    import numpy as np
    new = np.eye(4)
    ones = np.array([[1], [2], [3], [1]])
    trans = np.column_stack((new[:,0:3],ones))
    print(trans)
    print('Test complete')
