import slicer
from slicer.parameterNodeWrapper import isParameterPack


def copyNode(src, dest):
    # Clones src into dest, but keeps dest's display and storage nodes, if any
    # If neither src nor dest has display nodes, the default are created
    if src is not None and dest is not None:
        name = dest.GetName()
        if dest.IsA('vtkMRMLDisplayableNode'):
            displayNodesIDs = [dest.GetNthDisplayNodeID(n) for n in range(dest.GetNumberOfDisplayNodes())]
            storageNodesIDs = [dest.GetNthStorageNodeID(n) for n in range(dest.GetNumberOfStorageNodes())]

        dest.Copy(src)
        dest.SetName(name)

        if dest.IsA('vtkMRMLDisplayableNode'):
            dest.RemoveAllDisplayNodeIDs()
            for n, displayNodeID in enumerate(displayNodesIDs):
                dest.SetAndObserveNthDisplayNodeID(n, displayNodeID)
            for n, storageNodeID in enumerate(storageNodesIDs):
                dest.SetAndObserveNthStorageNodeID(n, storageNodeID)


def copyParameterPack(from_, to, nodeMapping=None):
    topLevel = nodeMapping is None
    nodeMapping: dict[slicer.vtkMRMLNode,
                      slicer.vtkMRMLNode] = nodeMapping or dict()
    for paramName in from_.allParameters:
        if isinstance(from_.getValue(paramName), slicer.vtkMRMLNode):
            fromNode, toNode = from_.getValue(paramName), to.getValue(paramName)
            copyNode(fromNode, toNode)
            nodeMapping[fromNode] = toNode
        elif isParameterPack(from_.getValue(paramName)):
            copyParameterPack(from_.getValue(paramName), to.getValue(paramName), nodeMapping)
        else:
            to.setValue(paramName, from_.getValue(paramName))

    if topLevel:
        for fromNode, toNode in nodeMapping.items():
            fromRoles = []
            fromNode.GetNodeReferenceRoles(fromRoles)
            for role in fromRoles:
                numRoleRefs = fromNode.GetNumberOfNodeReferences(role)
                for n in range(numRoleRefs):
                    ref = fromNode.GetNthNodeReference(role, n)
                    if ref in nodeMapping:
                        toNode.SetNthNodeReferenceID(role, n, nodeMapping[ref].GetID())


_directCopyTypes = (int, float, bool, str, type(None))


def _smartCopyImpl(from_, to, nodeMapping):
    """
    Assumes from and to are the same container type.
    """
    assert type(from_) == type(to)
    if isinstance(from_, slicer.vtkMRMLNode):
        print("Copy node", from_.GetName())
        copyNode(from_, to)
        nodeMapping[from_] = to
    elif isParameterPack(from_):
        print("Copy param pack", from_.__class__.__name__)
        for paramName in from_.allParameters.keys():
            print("Copy param", paramName)
            value = from_.getValue(paramName)
            if isinstance(value, _directCopyTypes):
                # direct copy primitive
                to.setValue(paramName, value)
            else:
                # smart copy anything else
                _smartCopyImpl(value, to.getValue(paramName), nodeMapping)
    elif isinstance(from_, dict):
        raise RuntimeError("Implement dictionary copy!")
    elif isinstance(from_, list):
        listCopy = []
        for f in from_:
            
    else:
        


        raise RuntimeError(f"Not smart enough to copy! {from_}")


def smartCopy(from_, toPack):
    """
    For use by generated widgets.

    Copies from the output of the logic, whatever that may be, to the <Pipeline>Outputs
    parameter pack
    """
    nodeMapping = dict()
    if isinstance(from_, type(toPack)):
        # this will always be true for multiple output
        print("Multiple output")
        _smartCopyImpl(from_, toPack, nodeMapping)
    else:
        # single output
        paramName = next(iter(toPack.allParameters.keys()))
        if isinstance(from_, _directCopyTypes):
            toPack.setValue(paramName, from_)
        if isParameterPack(from_):
            # A parameter pack, but not the output one
            _smartCopyImpl(from_, toPack.getValue(paramName), nodeMapping)
