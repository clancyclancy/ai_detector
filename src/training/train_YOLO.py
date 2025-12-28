# Datasets from:    
# https://huggingface.co/datasets/Hemg/AI-Generated-vs-Real-Images-Datasets
# https://www.kaggle.com/datasets/ayushmandatta1/deepdetect-2025?resource=download
#
#PS C:\Users\clanc\VSCode\ai_detector> python -m pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
# nightly cu128 supports 50 series gpus

# pyright: ignore[reportPrivateImportUsage]
from ultralytics import YOLO # type: ignore


from src.config import PROCESSED_DATA_DIR, MODEL_PATH
import os
import torch
torch.backends.cudnn.enabled = False


def train_model():

    # yolov8n-cls.pt is the smallest classification model
    model = YOLO('yolov8n-cls.pt') 

    # Train the model
    results = model.train(
        data=PROCESSED_DATA_DIR, 
        epochs  = 50, 
        imgsz   = 320, # if training too slow or accuracy high. i beleive the standard for class tasks is 224. why? idk
        batch   = 32,  # TODO: up to 32
        workers = 8,   # PS $env:NUMBER_OF_PROCESSORS 24
        device  = 0,   # use 0 for GPU
        project = os.path.dirname(MODEL_PATH),
        name    = 'ai_detector_run',
        amp     = False      # crash fix attempt
        #pin_memory = False,  # crash fix attempt. not exposed 

    )
    
if __name__ == "__main__":
    train_model()
