import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import numpy

#
# Kyle
#

class Kyle(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Kyle" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["John Doe (AnyWare Corp.)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    It performs a simple thresholding on the input volume and optionally captures a screenshot.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.

#
# KyleWidget
#

class KyleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

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
    # EM selector
    #
    self.emSelector = slicer.qMRMLNodeComboBox()
    self.emSelector.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.emSelector.setMRMLScene( slicer.mrmlScene )
    parametersFormLayout.addRow("EM Tool Tip Transform: ", self.emSelector)

    #
    # Optical selector
    #
    self.opSelector = slicer.qMRMLNodeComboBox()
    self.opSelector.nodeTypes = ["vtkMRMLLinearTransformNode"]
    self.opSelector.setMRMLScene( slicer.mrmlScene )
    parametersFormLayout.addRow("Optical Tool Tip Transform: ", self.opSelector)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.emSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    self.opSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def onTransformModified(self,caller,event):
    print('Transform modified')
    emTipTransform = self.emSelector.currentNode()
    if emTipTransform == None:
      return
    opTipTransform = self.opSelector.currentNode()
    if opTipTransform == None:
      return
    
    emTip = [0,0,0,1]
    opTip = [0,0,0,1]

    emTipToRasMat = vtk.vtkMatrix4x4()
    emTipTransform.GetMatrixTransformToWorld(emTipToRasMat)
    emTip_Ras = numpy.array(emTipToRasMat.MultiplyFloatPoint(emTip))

    opTipToRasMat = vtk.vtkMatrix4x4()
    opTipTransform.GetMatrixTransformToWorld(opTipToRasMat)
    opTip_Ras = numpy.array(opTipToRasMat.MultiplyFloatPoint(opTip))

    distance = numpy.linalg.norm(emTip_Ras - opTip_Ras)
    print(distance)
    return distance

  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.emSelector.currentNode() and self.opSelector.currentNode()
    

  def onApplyButton(self):
    #logic = KyleLogic()
    emTipTransform = self.emSelector.currentNode()
    if emTipTransform == None:
      return
    opTipTransform = self.opSelector.currentNode()
    if opTipTransform == None:
      return

    emTipTransform.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, self.onTransformModified)
    opTipTransform.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, self.onTransformModified)
    #enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    #imageThreshold = self.imageThresholdSliderWidget.value
    #logic.run(self.emSelector.currentNode(), self.opSelector.currentNode())

#
# KyleLogic
#

class KyleLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
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

  def run(self, inputVolume, outputVolume):
    """
  (self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
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
      self.takeScreenshot('KyleTest-Start','MyScreenshot',-1)
  
    logging.info('Processing completed')

    return True

  def GenerateTransformPoints(self,N,err):
    #Jan 24
    ReferenceToRas = slicer.vtkMRMLLinearTransformNode()
    ReferenceToRas.SetName('ReferenceToRas')
    slicer.mrmlScene.AddNode(ReferenceToRas)

    #Jan 26
    Scale = 100.0
    Sigma = err
    fromNormCoordinates = numpy.random.rand(N, 3)
    noise = numpy.random.normal(0.0, Sigma, N*3)
    RasFids = slicer.vtkMRMLMarkupsFiducialNode()
    RasFids.SetName('RasPoints')
    slicer.mrmlScene.AddNode(RasFids)
    ReferenceFids = slicer.vtkMRMLMarkupsFiducialNode()
    ReferenceFids.SetName('ReferencePoints')
    slicer.mrmlScene.AddNode(ReferenceFids)
    ReferenceFids.GetDisplayNode().SetSelectedColor(1,1,0)
    RasPoints = vtk.vtkPoints() #Used for registration
    ReferencePoints = vtk.vtkPoints()
    for i in range(N):
      x = (fromNormCoordinates[i, 0] - 0.5) * Scale
      y = (fromNormCoordinates[i, 1] - 0.5) * Scale
      z = (fromNormCoordinates[i, 2] - 0.5) * Scale
      RasFids.AddFiducial(x, y, z) #For visualization in 
      RasPoints.InsertNextPoint(x, y, z)
      xx = x+noise[i*3]
      yy = y+noise[i*3+1]
      zz = z+noise[i*3+2]
      ReferenceFids.AddFiducial(xx, yy, zz)
      ReferencePoints.InsertNextPoint(xx, yy, zz)
      slicer.mrmlScene.RemoveNode(ReferenceFids)
      slicer.mrmlScene.RemoveNode(RasFids)
    return [ReferencePoints,RasPoints,ReferenceToRas]


  def registration(self,ReferencePoints,RasPoints,ReferenceToRas):
    #Jan 31: Create landmark transform object that computes registration
    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetSourceLandmarks( RasPoints )
    landmarkTransform.SetTargetLandmarks( ReferencePoints )
    landmarkTransform.SetModeToRigidBody()
    landmarkTransform.Update()
    ReferenceToRasMatrix = vtk.vtkMatrix4x4()
    landmarkTransform.GetMatrix( ReferenceToRasMatrix )
    det = ReferenceToRasMatrix.Determinant()
    if det < 1e-8:
      print 'Unstable registration. Check input for collinear points.'
    ReferenceToRas.SetMatrixTransformToParent(ReferenceToRasMatrix)
    #averageDistance = logic.avgerageDistancePoints(RasPoints,ReferencePoints,ReferenceToRasMatrix)
    return ReferenceToRasMatrix 


    #print(catheterPosition_Ras)
    #Artery = slicer.vtkMRMLMarkupsFiducialNode()
    #Artery.GetNthFiducialWorldCoordinates(1, double coords[4])
    #Artery.AddFiducial(1,2,3)
  def avgerageDistancePoints(self,RasPoints,ReferencePoints,ReferenceToRasMatrix):
    # Compute average point distance after registration
    average = 0.0
    numbersSoFar = 0
    N = RasPoints.GetNumberOfPoints()
    for i in range(N):
      numbersSoFar = numbersSoFar + 1
      ras = RasPoints.GetPoint(i)
      pointA_Ras = numpy.array(ras)
      pointA_Ras = numpy.append(pointA_Ras, 1)
      pointA_Reference = ReferenceToRasMatrix.MultiplyFloatPoint(pointA_Ras)
      ref = ReferencePoints.GetPoint(i)
      pointB_Ref = numpy.array(ref)
      pointB_Ref = numpy.append(pointB_Ref, 1)
      distance = numpy.linalg.norm(pointA_Ras - pointB_Ref)
      average = average + (distance - average) / numbersSoFar
    #print "Average distance after registration: " + str(average)
    return average

  def TRE(self,ReferenceToRasMatrix):
    #Feb 2: Computes the target registration error
    targetPoint_Reference = numpy.array([0,0,0,1])
    targetPoint_Ras = ReferenceToRasMatrix.MultiplyFloatPoint(targetPoint_Reference)
    distance = numpy.linalg.norm(targetPoint_Reference - targetPoint_Ras)
    #print('TRE = ' + str(distance))
    return distance


class KyleTest(ScriptedLoadableModuleTest):
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
    self.setUp()
    self.test_Kyle1()

  def test_Kyle1(self):
    logic = KyleLogic()
    #Jan 27
    #Create Models
    createModelsLogic = slicer.modules.createmodels.logic()
    RasModelNode = createModelsLogic.CreateCoordinate(20,2)
    RasModelNode.SetName('RasCoordinateModel')
    ReferenceModelNode = createModelsLogic.CreateCoordinate(20,2)
    ReferenceModelNode.SetName('ReferenceCoordinateModel')

    #Set colours
    RasModelNode.GetDisplayNode().SetColor(1,0,0)
    ReferenceModelNode.GetDisplayNode().SetColor(0,0,1)

    #Transform Reference Node
    ReferenceModelToRas = slicer.vtkMRMLLinearTransformNode()
    ReferenceModelToRas.SetName('ReferenceModelToRas')
    slicer.mrmlScene.AddNode(ReferenceModelToRas)
    ReferenceModelNode.SetAndObserveTransformNodeID(ReferenceModelToRas.GetID())

    #Feb 7
    def avgDistanceAndTRE():
      FREs = []
      TREs = []
      numPoints = range(10,60,5)
      len_numPoints = len(numPoints)
      error = 3.0
      for num in numPoints:
        [ReferencePoints,RasPoints,ReferenceToRas] = logic.GenerateTransformPoints(num,error)
        ReferenceToRasMatrix = logic.registration(ReferencePoints,RasPoints,ReferenceToRas)
        FRE = logic.avgerageDistancePoints(RasPoints,ReferencePoints,ReferenceToRasMatrix)
        print "Average distance: " + str(FRE)
        FREs.append(FRE)
        TRE = logic.TRE(ReferenceToRasMatrix)
        print("TRE = " + str(TRE))
        TREs.append(TRE)


      #Feb 9
      lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
      lns.InitTraversal()
      ln = lns.GetNextItemAsObject()
      ln.SetViewArrangement(24)
      # Get the Chart View Node
      cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
      cvns.InitTraversal()
      cvn = cvns.GetNextItemAsObject()
      # Create an Array Node and add some data
      TRE_dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
      arrayTRE =TRE_dn.GetArray()
      arrayTRE.SetNumberOfTuples(len_numPoints)
      for i in range(len_numPoints):
          arrayTRE.SetComponent(i, 0, numPoints[i])
          arrayTRE.SetComponent(i, 1, TREs[i])
          arrayTRE.SetComponent(i, 2, 0)
      # Create a Chart Node.
      cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
      # Add the Array Nodes to the Chart. The first argument is a string used for the legend and to refer to the Array when setting properties.
      cn.AddArray('TRE', TRE_dn.GetID())

      # Set a few properties on the Chart. The first argument is a string identifying which Array to assign the property. 
      # 'default' is used to assign a property to the Chart itself (as opposed to an Array Node).
      cn.SetProperty('default', 'title', 'TRE')
      cn.SetProperty('default', 'xAxisLabel', 'Number of Points')
      cn.SetProperty('default', 'yAxisLabel', 'Units')

      # Tell the Chart View which Chart to display
      cvn.SetChartNodeID(cn.GetID()) 
    avgDistanceAndTRE()
    print('Test complete')
