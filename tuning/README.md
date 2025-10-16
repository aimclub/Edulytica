# Notebooks for model's tunig

## Description

This notebooks present code with tuning LLM that we used in experiments.

## Usage

You can run this notebooks in cloud, for example in Google Colab, or locally.

### For local using:
* Make sure that your device support cuda and cuda is installed. Check cuda installation guide for more information

Cuda installation guide for Windows: https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/

Cuda installation guide for Linux: https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/

For our models we used cuda version 12.1.105

You can check cuda version with run in cmd:
```
nvcc --version
```

* Check that python can use cuda and right version of pytorch has been installed. You can chek it with:
```
import torch


print("CUDA Available:", torch.cuda.is_available())
print("PyTorch CUDA Version:", torch.version.cuda)
```

You should get somethin like:

```
CUDA Available: True
PyTorch CUDA Version: 12.1
```
* If during tokenizer loading you get following error:
```
OSError: Unable to load vocabulary from file. Please check that the provided vocabulary is accessible and not corrupted.
```
Try to add:
```aiignore
use_fast=False
```
For example:
```aiignore
# OSError
llama_tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
#No error
llama_tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True, use_fast=False)
```
### For cloud using:

Usually in Google Colab all dependencies already installed. In case you have some issue, please check versions of cuda,
libraries and frameworks that you use.