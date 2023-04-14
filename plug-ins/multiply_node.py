import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    # Tell this program uses maya Python API 2.0
    pass


class MultiplyNode(om.MPxNode):  # Locator drawn in viewport but is not renderable

    TYPE_NAME = "multiplynode"    # Used when saved as maya ASCII
    TYPE_ID = om.MTypeId(0x0007f7f8)    # Used when saved as maya Binary

    multiplier_obj = None
    multiplicand_obj = None
    product_obj = None

    def __init__(self):
        super(MultiplyNode, self).__init__()

    def compute(self, plug, data):

        if plug == MultiplyNode.product_obj:
            multiplier = data.inputValue(MultiplyNode.multiplier_obj).asInt()
            multiplicand = data.inputValue(MultiplyNode.multiplicand_obj).asDouble()
            product = multiplier * multiplicand

            product_data_handle = data.outputValue(MultiplyNode.product_obj)
            product_data_handle.setDouble(product)

            data.setClean(plug)
        else:
            om.MGlobal.displayError("Plug is Dirty: {0}".format(plug))

    @classmethod
    def creator(cls):
        return MultiplyNode()    # Returns instance of our class

    @classmethod
    def initialize(cls):    # Initialize attributes of new node type

        numeric_attr = om.MFnNumericAttribute()

        cls.multiplier_obj = numeric_attr.create("multiplier", "mul", om.MFnNumericData.kInt, 2)
        numeric_attr.keyable = True
        numeric_attr.readable = False

        cls.multiplicand_obj = numeric_attr.create("multiplicand", "mulc", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.keyable = True
        numeric_attr.readable = False

        cls.product_obj = numeric_attr.create("product", "prod", om.MFnNumericData.kDouble, 0.0)
        numeric_attr.keyable = False
        numeric_attr.writable = False

        cls.addAttribute(cls.multiplier_obj)
        cls.addAttribute(cls.multiplicand_obj)
        cls.addAttribute(cls.product_obj)

        cls.attributeAffects(cls.multiplier_obj, cls.product_obj)
        cls.attributeAffects(cls.multiplicand_obj, cls.product_obj)


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


