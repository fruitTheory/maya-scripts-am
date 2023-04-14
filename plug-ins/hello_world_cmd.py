import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    # Tell this program uses maya Python API 2.0
    pass


class HelloWorldCmd(om.MPxCommand):

    COMMAND_NAME = "HelloWorld"    # Stores command name

    def __init__(self):
        super(HelloWorldCmd, self).__init__()   # To call MPxCommand init method

    def doIt(self, args):   # doIt() is required for ALL MPxCommands
        print("Hello World!!")  # All logic for command is implemented under doiT()

    @classmethod
    def creator(cls):
        return HelloWorldCmd()  # Gets new instance of this class/command


def initializePlugin(plugin):

    vendor = "Derwin"
    version = "1.0.0"

    pluginFn = om.MFnPlugin(plugin, vendor, version)    # Initialize plugin function set

    try:    # Try registering node, (command name, create command function)
        pluginFn.registerCommand(HelloWorldCmd.COMMAND_NAME, HelloWorldCmd.creator)
    except:    # Globally display error.. string format to name of class
        om.MGlobal.displayError("failed to register: {0}".format(HelloWorldCmd))


def uninitializePlugin(plugin):

    pluginFn = om.MFnPlugin(plugin)    #
    try:
        pluginFn.deregisterCommand(HelloWorldCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("failed to deregister: {0}".format(HelloWorldCmd))
    pass

