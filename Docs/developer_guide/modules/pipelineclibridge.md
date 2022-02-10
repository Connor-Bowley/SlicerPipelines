# Pipeline CLI Bridge Developer Guide

This module is used by the PipelineModule's CLIModuleWrapping and is not intended to be directly used by anything else. It's sole purpose is to bridge the gap between the CLI module's `qSlicerCLIModuleUIHelper` C++ code and pipeline's Python code.

For some commentary on the design and choices made by the Pipeline CLI Bridge, see [this link](https://github.com/KitwareMedical/SlicerPipelines/blob/main/PipelineCLIBridge/BridgeParameters/README.md).
