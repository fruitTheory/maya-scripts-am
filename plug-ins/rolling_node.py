import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    # Tell this program uses maya Python API 2.0
    pass


class RollingNode(om.MPxNode):  # Locator drawn in viewport but is not renderable

    TYPE_NAME = "rollingnode"  # Used when saved as maya ASCII
    TYPE_ID = om.MTypeId(0x0007f7f9)  # Used when saved as maya Binary

    distance_obj = None
    radius_obj = None
    rotation_obj = None
    randomChange = None

    def __init__(self):
        super(RollingNode, self).__init__()

    def compute(self, plug, data):
        if plug == self.rotation_obj:
            distance = data.inputValue(RollingNode.distance_obj).asDouble()
            radius = data.inputValue(RollingNode.radius_obj).asDouble()

            if radius == 0:
                rotation = 0
            else:
                rotation = distance / radius

            rotation_data_handle = data.outputValue(RollingNode.rotation_obj)
            rotation_data_handle.setDouble(rotation)

            data.setClean(plug)

    @classmethod
    def creator(cls):
        return RollingNode()  # Returns instance of our class

    @classmethod
    def initialize(cls):  # Initialize attributes of new node type
        numeric_attr = om.MFnNumericAttribute()

        cls.distance_obj = numeric_attr.create("distance", "dist", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.readable = False
        numeric_attr.keyable = True

        cls.radius_obj = numeric_attr.create("radius", "rad", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.readable = False
        numeric_attr.keyable = True

        unit_attr = om.MFnUnitAttribute()

        cls.rotation_obj = unit_attr.create("rotation", "rot", om.MFnUnitAttribute.kAngle, 0.0)

        cls.addAttribute(cls.distance_obj)
        cls.addAttribute(cls.radius_obj)
        cls.addAttribute(cls.rotation_obj)

        cls.attributeAffects(cls.distance_obj, cls.rotation_obj)
        cls.attributeAffects(cls.radius_obj, cls.rotation_obj)


def initializePlugin(plugin):  # Entry point for plugin

    vendor = "Derwin Prince"
    version = "1.0.0"
    api_version = "Any"

    plugin_fn = om.MFnPlugin(plugin, vendor, version, api_version)

    try:
        plugin_fn.registerNode(RollingNode.TYPE_NAME,
                               RollingNode.TYPE_ID,
                               RollingNode.creator,
                               RollingNode.initialize,
                               om.MPxNode.kDependNode)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(RollingNode.TYPE_NAME))
    else:
        om.MGlobal.displayInfo("Successfully registered node: {0}".format(RollingNode.TYPE_NAME))


def uninitializePlugin(plugin):  # Exit point for plugin

    plugin_fn = om.MFnPlugin(plugin)

    try:
        plugin_fn.deregisterNode(RollingNode.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to deregister node: {0}".format(RollingNode.TYPE_NAME))
    else:
        om.MGlobal.displayInfo("Successfully deregistered node: {0}".format(RollingNode.TYPE_NAME))


if __name__ == "__main__":
    # Any code required before unloading the plug-in (e.g. creating a new scene)
    cmds.file(new=True, force=True)

    # Reload the plugin
    plugin_name = "rolling_node.py"

    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    # Any setup code to help speed up testing (e.g. loading a test scene)
    # cmds.evalDeferred('cmds.createNode("rollingnode")')
    cmds.evalDeferred(
        'cmds.file("C:/Users/Derwin/Documents/maya/projects/default/scenes/wheel_plugin_testing.ma", open=True, force=True)')
