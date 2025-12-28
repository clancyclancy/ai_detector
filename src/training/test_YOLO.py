import argparse
import cv2
import os
from src.inference.explainability import GradCAMExplainer
from src.config import MODEL_PATH

def main():     
    parser = argparse.ArgumentParser()  
    parser.add_argument("image_path", type=str)
    parser.add_argument("--model",    type=str, default = MODEL_PATH)     
    parser.add_argument("--output",   type=str, default = "result.jpg")
      
 
    args = parser.parse_args()
    

    if not os.path.exists(args.image_path):
        print("path dne")
        return


    print(f"Loading model from {args.model}...")
    explainer = GradCAMExplainer(args.model)
    

    print(f"Analyzing {args.image_path}...")
    result     = explainer.get_prediction(args.image_path) # run
    top1_index = result.probs.top1                         # get predicted class ind  
    top1_conf  = result.probs.top1conf.item()              # confidence score of top class
    class_name = result.names[top1_index]                  # name

   
    print(f"Prediction: {class_name.upper()} ({top1_conf:.2%})")
    

    print("Generating heatmap...")
    visualization = explainer.cam_heatmap(args.image_path, target_category=top1_index)     
        

    cv2.imwrite(args.output, cv2.cvtColor(visualization, cv2.COLOR_RGB2BGR))  
    print(f"Saved to {args.output}")   
  

  
if __name__ == "__main__":  
    main() 


