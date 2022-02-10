# Pipeline Creator Developer Guide

:::{note}

All links linking to Github point to the master branch, so they may be out of date if this is an older version of the documentation.

:::

## Making a module available to the Pipeline Creator

The Pipeline Creator expects pipeline-able modules to have a certain interface. The module can either implement this directly (which is what pipelines created by the Pipeline Creator do) or a wrapper can be provided (which is what we do for most core modules and extensions, such as the Surface Toolbox).

The interface the Pipeline Creator expects is the `PipelineInterface` found in [this file](https://github.com/KitwareMedical/SlicerPipelines/blob/main/PipelineCreator/PipelineCreatorLib/PipelineBases.py). To make your module (or wrapper) available to the Pipeline Creator, simply inherit from `PipelineInterface`, implement the abstract methods, and decorate your class with the `@slicerPipeline` decorator. See [Full example](#full-example).

The `@slicerPipeline` decorator will register your module with the pipeline creator after all the dependencies given by `GetDependencies()` have been loaded with factory.

:::{note}

Because all the dependencies need to be loaded before a module is registered with the Pipeline Creator, if a dependency is missing, the module will never register with the Pipeline Creator.

:::

### Method Descriptions

| Method name | Return type | Description |
| :---        | :---        | :---        |
| GetName | string | Gets a unique name for the pipeline. Can have spaces. |
| GetInputType | string | The input MRML node type as a string that can be passed directly to `slicer.mrmlScene.AddNewNodeByClass`. |
| GetOutputType | string | The output MRML node type as a string that can be passed directly to `slicer.mrmlScene.AddNewNodeByClass`. Can be the same as the input type. |
| GetDependencies | list of strings | Gets the list of modules this module depends on. A dependency on PipelineCreator is implied and need not be listed. |
| SetProgressCallback | callable | Sets a callback to call when progress is updated. The callback must be given one parameter of type `PipelineProgress` and should return nothing. |
| Set\<paramName> | None | For each parameter in `GetParameters` there should be a corresponding `Set` method that takes the value of that parameters `GetValue()`.
| GetParameters | List of tuples | Parameters that the pipeline takes. Each tuple must be two or three members of the form `(paramName:str, param:paramType)` or `(paramName:str, paramLabel:str, param:paramType)` where `paramType` is an object that contains: 1. a `GetUI()` method that takes no parameters and returns a QWidget or QLayout; 2. a `GetValue()` method returns a value that can be passed directly to `Set<paramName>`. <br/><br/>Note: `paramName` may contain spaces. If it does, the corresponding `Set<paramName>` method will be as if the spaces were not there. E.g. parameter `("Smoothing Method", ...)` needs a corresponding `SetSmoothingMethod` method.
| Run | MRML node | Runs the module and returns a MRML node that matches the type given by `GetOutputType()`. Takes one parameter of a MRML node that matches the type given by `GetInputType()`.

### Full example:

```python
from PipelineCreator import slicerPipeline
from PipelineCreatorLib.PipelineBases import PipelineInterface

class IntegerParameter(object):
  def __init__(self, startValue=None):
    self._spinbox = qt.QSpinBox()
    if startValue is not None:
      self._spinbox.value = startValue

  def GetUI(self):
    return self._spinbox

  def GetValue(self):
    return self._spinbox.value

@slicerPipeline
class MyModule(PipelineInterface):
  @staticmethod
  def GetName():
    return "My Module Name"
  
  @staticmethod
  @abc.abstractmethod
  def GetParameters():
    return [
      ("MyFirstParameter", IntegerParameter(startValue=4)),
      ("MySecondParameter" "My nice label", IntegerParameter(startValue=7)),
    ]

  @staticmethod
  @abc.abstractmethod
  def GetInputType():
    return "vtkMRMLModelNode"

  @staticmethod
  @abc.abstractmethod
  def GetOutputType():
    return "vtkMRMLModelNode"

  @staticmethod
  @abc.abstractmethod
  def GetDependencies():
    return ['Models']

  @abc.abstractmethod
  def Run(self, inputNode):
    pass

  @abc.abstractmethod
  def SetProgressCallback(self, cb):
    pass
  ...

```

:::{important}

When returning values from `GetParameters`, make sure a separate QWidget is returned each time the method is called, or your module won't be able to be called twice in the same pipeline.

:::

## Helper classes

A number of helper classes are offered to allow easier creation of new Pipelines. For more helper classes see the [PipelineModules](pipelinemodules.md)

### ProgressablePipeline

`ProgressablePipeline` (found in [this file](https://github.com/KitwareMedical/SlicerPipelines/blob/main/PipelineCreator/PipelineCreatorLib/PipelineBases.py)) extends `PipelineInterface` and implements the `SetProgressCallback`. Users of this class need to just implement `GetNumberOfPieces() -> int` to return the number of pieces in the pipeline, and call the provided `_Progress(self, moduleName, currentPipelinePieceNumber)` function to update progress.

### SinglePiecePipeline

`SinglePiecePipeline` (found in [this file](https://github.com/KitwareMedical/SlicerPipelines/blob/main/PipelineCreator/PipelineCreatorLib/PipelineBases.py)) extends `ProgressablePipeline` and is meant for pipelines that are made up of a single module that has no fine grain progress tracking. It will report 0% progress on start and 100% progress on finish. `SinglePiecePipeline` implements the `Run` method and adds a `_RunImpl(self, inputNode) -> outputNode` method that needs to be implemented.

