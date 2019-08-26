from masterTools.problemSolvingSubtools.solveCompatibilityOrderManually import ManualCompatibilityHelper
from masterTools.misc.MasterToolsProcessor import MasterToolsProcessor
dsPath = '/Users/rafalbuchner/Documents/repos/scripts/RoboFont3.0/+GOOGLE/master-tools/test_designSpace/mutatorSans-master/MutatorSans.designspace'
designspace = MasterToolsProcessor()
designspace.read(dsPath)
designspace.loadFonts()

testObj = ManualCompatibilityHelper( designspace=designspace )
