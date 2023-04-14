import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaRender as omr
import maya.cmds as cmds


def maya_useNewAPI():
    # Tell this program uses maya Python API 2.0
    pass


class HelloWorldNode(omui.MPxLocatorNode):  # Locator drawn in viewport but is not renderable

    TYPE_NAME = "helloworld"    # Used when saved as maya ASCII
    TYPE_ID = om.MTypeId(0x0007f7f7)    # Used when saved as maya Binary
    DRAW_CLASSIFICATION = "drawdb/geometry/helloworld"
    DRAW_REGISTRANT_ID = "HelloWorldNode"


    def __init__(self):
        super(HelloWorldNode, self).__init__()

    @classmethod
    def creator(cls):
        return HelloWorldNode()    # Returns instance of our class

    @classmethod
    def initialize(cls):    # Initialize attributes of new node type
        pass


class HelloWorldDrawOverride(omr.MPxDrawOverride):

    NAME = "HelloWorldDrawOverride"

    def __init__(self, obj):
        super(HelloWorldDrawOverride, self).__init__(obj, None, False)

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        pass

    def supportedDrawAPIs(self):
        return omr.MRenderer.kAllDevices

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        draw_manager.beginDrawable()
        draw_manager.text2d(om.MPoint(100, 100), "Hello World!!")
        draw_manager.endDrawable()

    @classmethod
    def creator(cls, obj):
        return HelloWorldDrawOverride(obj)


def initializePlugin(plugin):

    vendor = "Derwin"
    version = "1.0.0"
    api_version = "Any"

    plugin_fn = om.MFnPlugin(plugin, vendor, version, api_version)

    try:    # Try/Except is important for debugging, not necessary but useful
        plugin_fn.registerNode(HelloWorldNode.TYPE_NAME,
                               HelloWorldNode.TYPE_ID,
                               HelloWorldNode.creator,
                               HelloWorldNode.initialize,
                               om.MPxNode.kLocatorNode,
                               HelloWorldNode.DRAW_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(HelloWorldNode.TYPE_NAME))
    else:
        om.MGlobal.displayInfo("Successfully registered node: {0}".format(HelloWorldNode.TYPE_NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,
                                                      HelloWorldNode.DRAW_REGISTRANT_ID,
                                                      HelloWorldDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(HelloWorldDrawOverride.NAME))



def uninitializePlugin(plugin):

    plugin_fn = om.MFnPlugin(plugin)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,
                                                        HelloWorldNode.DRAW_REGISTRANT_ID)

    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(HelloWorldDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(HelloWorldNode.TYPE_ID)

    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(HelloWorldNode.TYPE_NAME))
    else:
        om.MGlobal.displayInfo("Successfully deregistered node: {0}".format(HelloWorldNode.TYPE_NAME))

