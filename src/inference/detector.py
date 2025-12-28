from ultralytics import YOLO # type: ignore
from src.config  import MODEL_PATH
import os


class AIDetector:

    def __init__(self, model_path=None):

        self.model_path = model_path or MODEL_PATH

        if not os.path.exists(self.model_path):
            raise ValueError(f"AIDetector initialization: model not found at {self.model_path}")
        else:
            self.model = YOLO(self.model_path)
 

    def predict_image(self, image_path):

         #run 
        all_result = self.model(image_path)  

        # predicaiton is in first element  
        result = all_result[0] 

        top1_index = result.probs.top1            # get predicted class ind  
        top1_conf  = result.probs.top1conf.item() # confidence score of top class
        class_name = result.names[top1_index]     # name
    

        return class_name, top1_conf 
    



