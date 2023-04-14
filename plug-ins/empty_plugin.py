import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    pass


def initializePlugin(plugin):
    vendor = "Derwin"
    version = "1.0.0"

    om.MFnPlugin(plugin, vendor, version)

    print("Hello Test 2")


def uninitializePlugin(plugin):
    pass


if __name__ == "__main__":

    plugin_name = "empty_plugin.py"
    cmds.evalDeferred(
        'if cmds.pluginInfo("{0}", query=True, loaded=True) : cmds unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred(
        'if not cmds.pluginInfo("{0}", query=True, loaded=True) : cmds loadPlugin("{0}")'.format(plugin_name))

