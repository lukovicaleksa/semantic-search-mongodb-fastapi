from enum import Enum
from sentence_transformers import SentenceTransformer
import torch


class TorchDevice(Enum):
    CPU = 'cpu'
    GPU = 'cuda'
    AUTO = None


# embedding model inference device, set AUTO for automatic selection
INFERENCE_DEVICE = TorchDevice.AUTO


# force usage of CPU/GPU (if available)
if INFERENCE_DEVICE == TorchDevice.CPU:
    # CPU inference
    selected_inference_device = TorchDevice.CPU.value
elif INFERENCE_DEVICE == TorchDevice.GPU and torch.cuda.is_available():
    # GPU inference
    selected_inference_device = TorchDevice.GPU.value
else:
    # AUTO inference
    selected_inference_device = TorchDevice.AUTO.value


embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=selected_inference_device)
embedding_vector_length = embedding_model.get_sentence_embedding_dimension()
