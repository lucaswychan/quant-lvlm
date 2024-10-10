import torch

import torch
import nvidia_smi

def get_available_gpu_idx():
    """
    Get the GPU index which have more than 90% free memory
    """
    # Initialize NVIDIA-SMI
    nvidia_smi.nvmlInit()

    # Get the number of available GPUs
    deviceCount = nvidia_smi.nvmlDeviceGetCount()

    for i in range(deviceCount):
        handle = nvidia_smi.nvmlDeviceGetHandleByIndex(i)
        info = nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
        
        # Check if the GPU has enough free memory (e.g., 90% free)
        if info.free / info.total > 0.9:
            # Try to allocate a small tensor on this GPU
            try:
                with torch.cuda.device(f'cuda:{i}'):
                    torch.cuda.current_stream().synchronize()
                    torch.cuda.empty_cache()
                    torch.cuda.memory.empty_cache()
                    test_tensor = torch.zeros((1,), device=f'cuda:{i}')
                    del test_tensor
                    return i
            except RuntimeError:
                # If allocation fails, move to the next GPU
                continue

    # If no available GPU is found
    return None

if __name__ == "__main__":
    # Usage
    available_gpu = get_available_gpu_idx()

    if available_gpu is not None:
        print(f"Available GPU index: {available_gpu}")
        # You can now use this GPU index in your PyTorch code
        device = torch.device(f'cuda:{available_gpu}')
    else:
        print("No available GPU found")