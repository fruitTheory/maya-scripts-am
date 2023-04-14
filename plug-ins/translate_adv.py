import maya.api.OpenMaya as om


node_name = "pCube1"
attribute_name = "translate"

selection_list = om.MSelectionList()
selection_list.add(node_name)

obj = selection_list.getDependNode(0)

if obj.hasFn(om.MFn.kTransform):
    transform_fn = om.MFnTransform(obj)

    plug = transform_fn.findPlug(attribute_name, False)

if plug.isCompound:
    for i in range(plug.numChildren()):
        child_plug = plug.child(i)

        attribute_value = child_plug.asDouble()
        print("{0}.{1}".format(child_plug, attribute_value))




