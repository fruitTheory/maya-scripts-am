import maya.api.OpenMaya as om


node_name = "pCube1"
attribute_name = "translateY"

selection_list = om.MSelectionList()
selection_list.add(node_name)

obj = selection_list.getDependNode(0)

if obj.hasFn(om.MFn.kTransform):
    transform_fn = om.MFnTransform(obj)

    # plug = transform_fn.findPlug(attribute_name, False)
    #
    # attribute_value = plug.asDouble()
    # print("{0}.{1}".format(plug, attribute_value))
    #
    # plug.setDouble(2.0)

    translation = transform_fn.translation(om.MSpace.kTransform)
    translation[1] = 2.0
    transform_fn.setTranslation(translation, om.MSpace.kTransform)


