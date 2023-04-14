import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    # Tell this program uses maya Python API 2.0
    pass


class MultiplyNode(om.MPxNode):  # Locator drawn in viewport but is not renderable

    TYPE_NAME = "multiplynode"    # Used when saved as maya ASCII
    TYPE_ID = om.MTypeId(0x0007f7f8)    # Used when saved as maya Binary

    def __init__(self):
        super(MultiplyNode, self).__init__()

    @classmethod
    def creator(cls):
        return MultiplyNode()    # Returns instance of our class

    @classmethod
    def initialize(cls):    # Initialize attributes of new node type
        pass


def initializePlugin(plugin):   # Entry point for plugin

    vendor = "Derwin Prince"
    version = "1.0.0"
    api_version = "Any"

    plugin_fn = om.MFnPlugin(plugin, vendor, version, api_version)

    try:
        plugin_fn.registerNode(MultiplyNode.TYPE_NAME,
                               MultiplyNode.TYPE_ID,
                               MultiplyNode.creator,
                               MultiplyNode.initialize,
                               om.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(MultiplyNode.TYPE_NAME))
    else:
        om.MGlobal.displayInfo("Successfully registered node: {0}".format(MultiplyNode.TYPE_NAME))


def uninitializePlugin(plugin):    # Exit point for plugin

    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(MultiplyNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(MultiplyNode.TYPE_NAME))
    else:
        om.MGlobal.displayInfo("Successfully deregistered node: {0}".format(MultiplyNode.TYPE_NAME))


