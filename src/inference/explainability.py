import numpy as np
import torch
import cv2
from pytorch_grad_cam             import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image, preprocess_image
from ultralytics                  import YOLO # type: ignore

from src.config import MODEL_TRAIN_IMAGE_SIZE 


# mismatch between YOLO and CAM
# add a check if model is outputting a tuple
class ModelWrapper(torch.nn.Module):

    def __init__(self, model): 
        super(ModelWrapper, self).__init__() 
        self.model = model
    

    def forward(self, x):
        output = self.model(x)
        if isinstance(output, tuple):
            return output[0]
        return output
    


class GradCAMExplainer:

    def __init__(self, model_path=None, model_instance=None):   

        if model_instance:
            self.yolo = model_instance

        elif model_path:
            self.yolo = YOLO(model_path)

        else:
            raise ValueError("Either model_path or model_instance must be provided")
            
        self.inner_model = self.yolo.model
        self.model = ModelWrapper(self.inner_model) # crash fix attempt

        # crash fix attempt: enable gradients for all parameters to ensure cam works
        for param in self.inner_model.parameters():
            param.requires_grad = True # 
            
        self.target_layers = [self.inner_model.model[9].conv] # last conv layer
  

    def cam_heatmap(self, image_path, target_category=None):
     
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (MODEL_TRAIN_IMAGE_SIZE, MODEL_TRAIN_IMAGE_SIZE)) # Resize to model's trained input size (the default is normally 224 for cls)   
        rgb_img = np.float32(img) / 255.0
        
        input_tensor = preprocess_image(rgb_img, mean=[0.0, 0.0, 0.0], std=[1.0, 1.0, 1.0])
        
        # Ensure input tensor is on the same device as the model
        device = next(self.model.parameters()).device
        input_tensor = input_tensor.to(device)
                
        input_tensor.requires_grad = True # crash fix attempt

        # 2. Run Grad-CAM
        # We need to ensure the model is in eval mode
        self.model.eval()
        
        # Construct the CAM object
        # use_cuda = torch.cuda.is_available()
        # We'll let pytorch_grad_cam handle device, but we should match model device
        
        with GradCAM(model=self.model, target_layers=self.target_layers) as cam:
            # If target_category is None use highest scoring category
            targets = None 
            if target_category is not None:  
                from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
                targets = [ClassifierOutputTarget(target_category)]

            with torch.enable_grad(): # allegedly this is NOT needed but it crashes sometimes
                grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
            
            grayscale_cam = grayscale_cam[0, :]
            
            visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
                
            return visualization

    def get_prediction(self, image_path):

        results = self.yolo(image_path)
        
        return results[0] # first is pred
