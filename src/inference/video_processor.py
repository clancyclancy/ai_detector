from src.inference.detector import AIDetector

class VideoProcessor:   
  
    def __init__(self, detector: AIDetector):       
        self.detector = detector  
  

    def process_video(self, video_path, frame_skip=30):
        # TODO: implement video processing and frame extraction 
        return []           