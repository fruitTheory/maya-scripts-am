from PySide2 import QtWidgets, QtCore, QtGui
from asset_manager_ui import Ui_MainWindow

import json
import os
import maya.cmds as cmds
import pymel.core as PM
import logging
import pprint
import maya.mel as mel
import mtoa.utils as mutils
import time

logging.basicConfig()
logger_ShaderManager = logging.getLogger("ShaderManager")
logger_ShaderManager.setLevel(logging.DEBUG)

logger_MainUI = logging.getLogger("MainUI")
logger_MainUI.setLevel(logging.DEBUG)

logger_ArnoldSnapshot = logging.getLogger("ArnoldSnapshot")
logger_ArnoldSnapshot.setLevel(logging.DEBUG)

DIRECTORY_lib = os.path.join(cmds.internalVar(userAppDir=True), "CustomLibrary")
DIRECTORY_lib_shaders = os.path.join(DIRECTORY_lib, "custom_shaders")
DIRECTORY_lib_geometry = os.path.join(DIRECTORY_lib, "custom_geometry")
DIRECTORY_lib_icons = os.path.join(DIRECTORY_lib_shaders, "shader_icons")


class ShaderManager(object):

    def __init__(self):
        self.createDir()
        self.shader_selection = None
        self.allowed_node_types = None
        self.sel_condition = True

    def createDir(self, directory=DIRECTORY_lib, directory_shaders=DIRECTORY_lib_shaders,
                  directory_assets=DIRECTORY_lib_geometry):
        # Creating base directory
        if not os.path.exists(directory):
            os.mkdir(directory)
            logger_ShaderManager.debug("Directory Created")

        # Creating sub directories
        if os.path.exists(directory):
            logger_ShaderManager.debug("Directory Exists")
            if not os.path.exists(directory_shaders):
                os.mkdir(directory_shaders)
            if not os.path.exists(directory_assets):
                os.mkdir(directory_assets)

        # Creating tertiary directories
        if os.path.exists(directory_shaders):
            if not os.path.exists(DIRECTORY_lib_icons):
                os.mkdir(DIRECTORY_lib_icons)

    def select_upstream(self):

        try:
            self.allowed_node_types = allowed_node_types = ["lambert", "blinn",
                                                            "aiStandardSurface", "VRayMtl"]
            self.shader_selection = selection = cmds.ls(selection=True)
            if not selection:
                raise ValueError("Select a Shader to Export - Ex:Lambert1")

            node_type = cmds.nodeType(selection)
            if node_type not in allowed_node_types:
                raise TypeError("{} is not an allowed type - Try using {}".format(node_type, allowed_node_types))

            # Get connections, set checkbox true if displacement is involved
            shader_connections = cmds.listConnections(source=True)
            displacement_check = True

            # Small loop to select shading engine if displacement map involved
            if displacement_check:
                for shader in shader_connections:
                    if shader.endswith("SG"):
                        cmds.select(shader, noExpand=True)
            '''
            Note on ShadingEngine:
                materialSG is an objectSet and cmds.select() defaults
                to selecting the members of that set rather than the set itself.
                You can subvert this behavior with the noExpand=True flag
            '''

        except RuntimeError:
            logger_ShaderManager.debug("Failed")

        logger_ShaderManager.debug("Success")

        # Now initialised as true
        sel_condition = self.sel_condition

        # Continues adding upstream nodes until network selection is fulfilled
        while sel_condition:
            selected = cmds.ls(selection=True)
            old_list = cmds.listConnections(selected, source=True, destination=False)
            # print old_list

            cmds.select(old_list, add=True)
            new_list = cmds.ls(selection=True)
            # print cmds.ls(selection=True)
            if len(new_list) == len(selected):
                sel_condition = False
                logger_ShaderManager.debug("Initialising Export")
                self.export_network(sel_condition)
                # Runs export method

    def export_network(self, sel_condition, directory_shaders=DIRECTORY_lib_shaders):

        if not sel_condition:
            current_shader_path = os.path.join(directory_shaders + "/", str(self.shader_selection[0]))
            cmds.file(current_shader_path, force=True, exportSelected=True, type="mayaAscii")
            logger_ShaderManager.debug("Exported: " + str(self.shader_selection[0]))
            self.store_shader_info()

    def store_shader_info(self, directory_shaders=DIRECTORY_lib_shaders, **shader_info):

        selected_shader = self.shader_selection[0]
        shader_json = os.path.join(directory_shaders, "{}.json".format(selected_shader))
        shader_file = os.path.join(directory_shaders, "{}.ma".format(selected_shader))
        node_type = cmds.nodeType(self.shader_selection)

        # This info can be pull in later if needed
        shader_info["node_type"] = node_type
        shader_info["shader_name"] = selected_shader
        shader_info["shader_path"] = shader_file
        with open(shader_json, "w") as f:
            json.dump(shader_info, f, indent=4)

        if node_type == self.allowed_node_types[2]:
            # Important setup for next series of executions
            cmds.select(self.shader_selection, replace=True)
            self.snap = SnapShot()
            self.snap.render_snapshot()


class LookEnvironment(object):

    def __init__(self):

        self.lookdev_object = None
        self.lookdev_name = None
        self.dome_light = None
        self.selected_shader = None

        # Set viewport to arnold
        mel.eval("setRendererAndOverrideInModelPanel $gViewport2 arnoldViewOverride modelPanel4")

    def create_environment(self):

        self.selected_shader = cmds.ls(selection=True)
        self.lookdev_object = cmds.polySphere(subdivisionsX=36, subdivisionsY=36, name="default_object_1")
        self.lookdev_name = cmds.ls(selection=True)

        self.dome_light = mutils.createLocator("aiSkyDomeLight", asLight=True)

        return self.lookdev_name, self.dome_light, self.selected_shader

    def set_environment(self):

        self.create_environment()

        # Setting object instance parameters - Only runs once
        lookdev_object = self.lookdev_name
        cmds.select(lookdev_object)
        shape = cmds.listRelatives(lookdev_object, shapes=True)
        shape_str = str(shape[0])

        cmds.setAttr(shape_str + ".aiSubdivType", 1)
        cmds.setAttr(shape_str + ".aiSubdivIterations", 2)

        cmds.hyperShade(assign=self.selected_shader[0])
        #
        # is_transparent = True
        # if is_transparent:
        #     cmds.setAttr(shape_str + ".aiOpaque", 0)

        # Setting dome light instance parameters - Only runs once
        dome_light = self.dome_light
        dome_str = str(dome_light[0])

        cmds.setAttr(dome_str + ".color", 1, 0.966667, 0.9, type="double3")
        cmds.setAttr(dome_str + ".intensity", 0.75)
        cmds.setAttr(dome_str + ".camera", 0)

        # Clear selection
        cmds.select(clear=True)

        logger_ArnoldSnapshot.debug("Creating Look Environment..")

        return self.lookdev_name, self.dome_light, self.selected_shader


class SnapShot(LookEnvironment):

    def __init__(self):
        super(SnapShot, self).__init__()

        self.selected_shader = cmds.ls(selection=True)[0]
        self.look = LookEnvironment()

        # self.render_snapshot()

    def render_snapshot(self):

        snap_lookenv = self.look.set_environment()
        '''
        Returns:
            ([u'default_object_X'], (u'|aiSkyDomeLightX|aiSkyDomeLightShapeX', u'aiSkyDomeLightX'))
        '''
        # Returned from set environment
        base_obj = snap_lookenv[0]
        base_light = snap_lookenv[1]

        logger_ArnoldSnapshot.debug("Snap")

        cmds.select(base_obj)
        cmds.viewFit()
        cmds.select(clear=True)

        # logger_ArnoldSnapshot.debug(self.selected_shader)
        # Start ipr render - Playblast - End ipr render
        render_on = True
        render_off = False
        if render_on:
            cmds.arnoldRenderView(opt=['Run IPR', '1'])
            cmds.setAttr("defaultRenderGlobals.imageFormat", 8)
            path = os.path.join(DIRECTORY_lib_icons, "{}.jpg".format(self.selected_shader))
            # logger_ArnoldSnapshot.debug(path)
            cmds.playblast(completeFilename=path, forceOverwrite=True, format="image",
                           showOrnaments=False, startTime=1, endTime=1, viewer=False)
            if not render_off:
                time.sleep(0.5)
                cmds.arnoldRenderView(opt=['Run IPR', '0'])
                render_complete = True
                if render_complete:
                    pass
                    # Cleanup object and dome light
                    logger_ArnoldSnapshot.debug("Deleting Look Environment..")
                    cmds.delete(base_obj)
                    cmds.delete(base_light)


class MainUI(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()

        # Pymel query main window, if already exists delete it
        if PM.workspaceControl("MainWindow", query=True, exists=True):
            PM.deleteUI("MainWindow")

        # Referencing Shader Class
        self.shade = ShaderManager()

        # Fundamental object class - Ui_MainWindow()
        self.ui = Ui_MainWindow()
        # SetupUi - Fundamental method of object class
        self.ui.setupUi(self)

        # Clean list on open
        self.refresh_network()

        # Initialise import - export buttons
        self.ui.pButton_import.clicked.connect(self.import_network)
        self.ui.pButton_export.clicked.connect(self.shade.select_upstream)
        self.ui.pButton_refresh.clicked.connect(self.refresh_network)
        self.ui.pButton_delete.clicked.connect(self.delete)
        self.ui.pButton_exit.clicked.connect(self.close)

        # Initialise list widget options
        size = 72 * 4
        self.ui.listWidget_shaders.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.ui.listWidget_shaders.setViewMode(QtWidgets.QListWidget.IconMode)
        self.ui.listWidget_shaders.setIconSize(QtCore.QSize(size, size))
        self.ui.listWidget_shaders.setGridSize(QtCore.QSize(size, size-52))

    def refresh_network(self):

        directory_shaders = DIRECTORY_lib_shaders
        directory_icons = DIRECTORY_lib_icons
        blinn_icon = os.path.join(directory_icons, "{}.jpg".format("blinn3"))
        # blinn_icon = "string"
        if not os.path.exists(blinn_icon):
            logger_MainUI.debug("Warning: Icon missing - {}".format(blinn_icon))

        if not os.path.exists(directory_shaders):
            return

        # Clear list before refill
        self.ui.listWidget_shaders.clear()

        files = os.listdir(directory_shaders)
        if not files:
            logger_MainUI.debug("Directory Empty")

        mayaFiles = [f for f in files if f.endswith(".ma")]
        if not mayaFiles:
            logger_MainUI.debug("No ASCII files found in Directory")

        names = []

        for ma in mayaFiles:
            name, trash = os.path.splitext(ma)
            names.append(name)

        for each_name in names:
            icon = QtGui.QIcon(blinn_icon)
            list_item = QtWidgets.QListWidgetItem(each_name)
            list_item.setIcon(icon)
            list_item.setToolTip(pprint.pformat(each_name))
            self.ui.listWidget_shaders.addItem(list_item)

    def import_network(self):

        try:
            current = self.ui.listWidget_shaders.currentItem()
            if current:
                network_name = current.text()
                directory_shaders = DIRECTORY_lib_shaders
                ext = ".ma"
                logger_MainUI.debug("Importing.. {}".format(network_name))
                cmds.file("{}/{}{}".format(directory_shaders, network_name, ext), i=True, usingNamespaces=False)
            else:
                raise ValueError("Select a shader to import")
        except RuntimeError:
            "Import Failed"

    def delete(self):
        directory_shaders = DIRECTORY_lib_shaders
        current_item = self.ui.listWidget_shaders.currentItem()

        if current_item:
            current_row = self.ui.listWidget_shaders.currentRow()
            network_name = current_item.text()

            self.ui.listWidget_shaders.takeItem(current_row)

            for filename in os.listdir(directory_shaders):
                if filename.startswith(network_name):
                    os.remove(os.path.join(directory_shaders, filename))
                    logger_MainUI.debug("Warning, Removed: {}".format(filename))


def showUI():
    window = MainUI()
    window.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
    window.show()

    return window

# Reminder to cast to variable:
# var = Class.showUI()
