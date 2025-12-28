"""
 split raw dataset into train, val, and test
 expected struct:
 data/raw/ 
        real/              
        ai/ 

"""
      

import os  
import shutil
import random   
from pathlib import Path 
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR 
  

# 70% train, 20% val, 10% test   
split_ratio = (0.7, 0.2, 0.1)
classes     = ['real', 'ai']


def split_dataset():

    
    for split in ['train', 'val', 'test']:
        for cls in classes:
            os.makedirs(os.path.join(PROCESSED_DATA_DIR, split, cls), exist_ok=True)

    for cls in classes:
        src_dir = os.path.join(RAW_DATA_DIR, cls)
        if not os.path.exists(src_dir):
            print("err: should not be here")
            continue

        # accept png,jpg,jpeg
        files = [f for f in os.listdir(src_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]        
        random.shuffle(files)  # probably should have set seed 
   
        train_count = int(len(files) * split_ratio[0])  
        val_count   = int(len(files) * split_ratio[1])  
        
        splits = {
            'train': files[:train_count],
            'val':   files[train_count:train_count + val_count],
            'test':  files[train_count + val_count:]
        }

        for split, split_files in splits.items():

            for file in split_files:
                src_file = os.path.join(src_dir, file)
                dst_file = os.path.join(PROCESSED_DATA_DIR, split, cls, file)
                shutil.copy2(src_file, dst_file)
          
        print(f"Processed {cls}: {len(splits['train'])} train, {len(splits['val'])} val, {len(splits['test'])} test")

   
   
if __name__ == "__main__": 
    split_dataset()   
    print("Dataset split completed.")  

   


