# Pipeline Modules Developer Guide

This module creates pipelines for many of the non-extension modules that are in 3D Slicer. In doing so, a number of classes were made that are available for use in creating other pipelines outside this module.

## Pipeline Parameters

The `PipelineInterface.GetParameters` method has a specific format it expects parameter types in. The [`PipelineParameters.py` file](https://github.com/KitwareMedical/SlicerPipelines/blob/main/PipelineModules/PipelineModulesLib/PipelineParameters.py) has classes that meet this interface (these classes are _available_ for use, but not _required_). They mostly wrap around Qt and CTK widgets. For the full list of available classes, see the [source code](https://github.com/KitwareMedical/SlicerPipelines/blob/main/PipelineModules/PipelineModulesLib/PipelineParameters.py).

Example usage:

```python
from PipelineCreator import slicerPipeline
from PipelineCreatorLib import PipelineInterface
from PipelineModulesLib.PipelineParameters import (
  IntegerParameterWithSlider,
  StringComboBoxParameter,
)

class MyNewPipeline(PipelineInterface):
  @staticmethod
  def GetParameters():
    return [
      ("Iterations", IntegerParameterWithSlider(value=100, minimum=1, maximum=500)),
      ("Smoothing Type", StringComboBoxParameter(['Median', 'Gaussian'])),
    ]

```

## CLI Module Wrapping

CLI Modules have the benefit of having a well defined interface. The `CLIModuleWrapping` does the job of converting from the CLI Module interface to the `PipelineInterface`. 

Currently the conversion is incomplete, so not all features available in the CLI modules can be used.

There are currently two methods in the `CLIModuleWrapping` that can be used.

### PipelineCLI

Registers a CLI module with the Pipeline Creator after all the CLI modules dependencies are loaded.

| Argument | Type | Required/Optional | Description |
| :---     | :--- | :---              | :---        |
| cliModuleName | string | Required | The name of the CLI module. |
| pipelineCreatorLogic | PipelineCreatorLogic | Optional | The pipeline creator to register to. If not specified, will register will the global instance (most common choice). |
| inputArgName | string | Optional | The name of the input argument. If not specified, an attempt to deduce it will be made on the grounds it must be a MRML node and be on the input channel. If the deduction fails, an exception will be thrown. |
| outputArgName | string | Optional | The name of the output argument. If not specified, an attempt to deduce it will be made on the grounds it must be a MRML node and be on the output channel. If the deduction fails, an exception will be thrown. |
| excludeArgs | list of strings | Optional | A list of argument names that should not be parameters in the pipeline. <br/><br/> An example usage of this is in `MeshToLabelMap`, the `reference` argument is a Volume, and MRML nodes can not currently be parameters to pipelines, so it is excluded and the `spacing` parameter is used instead. |

Example usage:

```python
try:
  from PipelineModulesLib.CLIModuleWrapping import PipelineCLI
  PipelineCLI("MyCLIModule", inputArgName="mesh", excludeArgs=['reference'])
except ImportError:
  pass
```

:::{note}

The rational behind putting this in a `try/except` block is that the code can be run without error in instances of Slicer where the SlicerPipelines extension is not present. This way your extension can be available as a pipeline without being dependent on (i.e. requiring) SlicerPipelines.

:::

See [MeshToLabelMap](https://github.com/slicersalt/MeshToLabelMap/blob/master/MeshToLabelMapPipeline/MeshToLabelMapPipeline.py) for an actual usage in an extension.
