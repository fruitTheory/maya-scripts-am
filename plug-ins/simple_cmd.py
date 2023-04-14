import maya.api.OpenMaya as om
import maya.cmds as cmds


def maya_useNewAPI():
    # Tell this program uses maya Python API 2.0
    pass


class SimpleCmd(om.MPxCommand):

    COMMAND_NAME = "SimpleCmd"    # Stores command name
    TRANSLATE_FLAG = ["-t", "-translate", (om.MSyntax.kDouble, om.MSyntax.kDouble, om.MSyntax.kDouble)]
    VERSION_FLAG = ["-v,", "-version"]
    # NAME_FLAG = ["-n", "-name"]

    def __init__(self):
        super(SimpleCmd, self).__init__()   # To call MPxCommand init method
        self.undoable = False

        # END_OF __init__()

    def doIt(self, args_list):
        try:
            arg_db = om.MArgDatabase(self.syntax(), args_list)
        except:
            self.displayError("Error parsing args")
            raise

        selection_list = arg_db.getObjectList()

        self.selected_obj = selection_list.getDependNode(0)

        if self.selected_obj.apiType() != om.MFn.kTransform:
            raise RuntimeError("This command requires a transform node.")

        self.edit = arg_db.isEdit
        self.query = arg_db.isQuery

        self.translate = arg_db.isFlagSet(SimpleCmd.TRANSLATE_FLAG[0])
        if self.translate:
            transform_fn = om.MFnTransform(self.selected_obj)
            self.orig_translation = transform_fn.translation(om.MSpace.kTransform)

            if self.edit:
                self.new_translation = [arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0], 0),
                                        arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0], 1),
                                        arg_db.flagArgumentDouble(SimpleCmd.TRANSLATE_FLAG[0], 2)]
                self.undoable = True

        self.version = arg_db.isFlagSet(SimpleCmd.VERSION_FLAG[0])

        self.redoIt()

        # Ctrl+Shift+ (numpad -) to minus // Ctrl+Shift+ (numpad +) to open up
        # version_flag_enabled = arg_db.isFlagSet(SimpleCmd.VERSION_FLAG[0])
            #         # if version_flag_enabled:
            #         #     # self.displayInfo("1.0.0")
            #         #     self.setResult("1.0.0")
            #         # else:
            #         #     # first_name = "SimpleCmd"
            #         #     # if arg_db.isFlagSet(SimpleCmd.NAME_FLAG[0]):
            #         #     #     first_name = arg_db.flagArgumentString(SimpleCmd.NAME_FLAG[0], 0)
            #         #     #     last_name = arg_db.flagArgumentString(SimpleCmd.NAME_FLAG[0], 1)
            #         #     #
            #         #     # # try:
            #         #     # #     first_name = arg_db.commandArgumentString(0)
            #         #     # #     last_name = arg_db.commandArgumentString(1)
            #         #     # # except:
            #         #     # #     first_name = "SimpleCmd"
            #         #     # #     last_name = ""
            #         #     # #
            #         #     #
            #         #     # self.displayInfo("doIt says: Hello {0} {1}".format(first_name, last_name))
            #         #     selection_list = arg_db.getObjectList()

            # for i in range(selection_list.length()):
            #     depend_fn = om.MFnDependencyNode(selection_list.getDependNode(i))
            #     print(depend_fn.name())

        # END_OF doIt()

    def undoIt(self):
        transform_fn = om.MFnTransform(self.selected_obj)
        transform_fn.setTranslation(om.MVector(self.orig_translation), om.MSpace.kTransform)

    def redoIt(self):
        transform_fn = om.MFnTransform(self.selected_obj)

        if self.query:
            if self.translate:
                self.setResult(self.orig_translation)
                self.displayInfo(str(self.orig_translation))
            else:
                raise RuntimeError("Flag does not support query.")
        elif self.edit:
            if self.translate:
                transform_fn.setTranslation(om.MVector(self.new_translation), om.MSpace.kTransform)
            else:
                raise RuntimeError("Flag does not support edit.")
        elif self.version:
            self.setResult("1.0.0")
        else:
            self.setResult(transform_fn.name())

        # END_OF redoIt()

    def isUndoable(self):
        return self.undoable

    @classmethod
    def creator(cls):
        return SimpleCmd()  # Returns instance of itself

    @classmethod
    def create_syntax(cls):    # This defines the syntax for the command Cmd(str1, str2)

        syntax = om.MSyntax()

        syntax.enableEdit = True
        syntax.enableQuery = True

        # Ctrl+Shift+ (numpad -) to minus // Ctrl+Shift+ (numpad +) to open up
        # syntax.addFlag(SimpleCmd.VERSION_FLAG[0], SimpleCmd.VERSION_FLAG[1])
        # syntax.addFlag(SimpleCmd.NAME_FLAG[0], SimpleCmd.NAME_FLAG[1], (om.MSyntax.kString, om.MSyntax.kString))

        # syntax.addArg(om.MSyntax.kString)    # Arg for string // these two for string int method
        # syntax.addArg(om.MSyntax.kUnsigned)   # Arg for unsigned integer

        # syntax.setObjectType(om.MSyntax.kSelectionList, 0, None)  # These two for select method
        # syntax.useSelectionAsDefault(True)

        syntax.addFlag(*cls.TRANSLATE_FLAG)
        syntax.addFlag(*cls.VERSION_FLAG)

        syntax.setObjectType(om.MSyntax.kSelectionList, 1, 1)
        syntax.useSelectionAsDefault(True)

        return syntax

        # END_OF create_syntax()


def initializePlugin(plugin):

    vendor = "Derwin"
    version = "1.0.0"

    pluginFn = om.MFnPlugin(plugin, vendor, version)    # Initialize plugin function set

    try:    # Try registering node, (command name, create command function)
        pluginFn.registerCommand(SimpleCmd.COMMAND_NAME, SimpleCmd.creator, SimpleCmd.create_syntax)
    except:    # Globally display error.. string format to name of class
        om.MGlobal.displayError("failed to register: {0}".format(SimpleCmd))


def uninitializePlugin(plugin):

    pluginFn = om.MFnPlugin(plugin)    #
    try:
        pluginFn.deregisterCommand(SimpleCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("failed to deregister: {0}".format(SimpleCmd))
    pass

