from ultralytics import YOLO # type: ignore
from src.config import MODEL_PATH, PROCESSED_DATA_DIR

def evaluate_model():
    model = YOLO(MODEL_PATH)    
    metrics = model.val(data=PROCESSED_DATA_DIR)
    print(f"Top-1 Accuracy: {metrics.top1}")
    print(f"Top-5 Accuracy: {metrics.top5}")    
    
if __name__ == "__main__":
    evaluate_model()
