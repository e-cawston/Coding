"""
YOLOv11 Beet Moth Detection Training Script for Google Colab
=============================================================
This script trains a YOLOv11 nano model on a Beet Moth dataset stored in Google Drive.
"""

#Copy and paste into collab. Set to T4GPU.

# ==================== STEP 1: Mount Google Drive ====================
print("=" * 60)
print("STEP 1: Mounting Google Drive")
print("=" * 60)

from google.colab import drive
drive.mount('/content/drive')

print("✓ Google Drive mounted successfully!\n")

# ==================== STEP 2: Install Ultralytics ====================
print("=" * 60)
print("STEP 2: Installing Ultralytics Library")
print("=" * 60)

!pip install ultralytics -q

print("✓ Ultralytics installed successfully!\n")


#New cell
# ==================== STEP 3: Setup Paths and Verify Dataset ====================
print("=" * 60)
print("STEP 3: Setting Up Paths and Verifying Dataset")
print("=" * 60)

import os
import yaml
from pathlib import Path

# Define paths
DRIVE_DATASET_PATH = '/content/drive/MyDrive/Euan_Work/BBRO/Data/AI_training/Beet_Moth_Project'
DRIVE_MODELS_PATH = '/content/drive/MyDrive/Euan_Work/BBRO/Data/AI_training/Beet_Moth_Project/models'

# Create models directory in Google Drive if it doesn't exist
os.makedirs(DRIVE_MODELS_PATH, exist_ok=True)

# Verify dataset structure
print(f"\nDataset location: {DRIVE_DATASET_PATH}")
print("\nDataset contents:")
for item in os.listdir(DRIVE_DATASET_PATH):
    print(f"  - {item}")

# Look for data.yaml file
yaml_path = os.path.join(DRIVE_DATASET_PATH, 'data.yaml')
if os.path.exists(yaml_path):
    print(f"\n✓ Found data.yaml at: {yaml_path}")
    
    # Read and display the YAML configuration
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    print("\nDataset configuration:")
    print(yaml.dump(config, default_flow_style=False))
    
    # Check if paths need to be updated for absolute paths
    needs_update = False
    if 'train' in config and not os.path.isabs(config['train']):
        needs_update = True
    if 'val' in config and not os.path.isabs(config['val']):
        needs_update = True
    
    if needs_update:
        print("\n⚠ Updating data.yaml with absolute paths...")
        
        # Update paths to be absolute
        if 'train' in config:
            config['train'] = os.path.join(DRIVE_DATASET_PATH, config['train'])
        if 'val' in config:
            config['val'] = os.path.join(DRIVE_DATASET_PATH, config['val'])
        if 'test' in config:
            config['test'] = os.path.join(DRIVE_DATASET_PATH, config['test'])
        
        # Save updated YAML
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✓ data.yaml updated with absolute paths")
else:
    print(f"\n⚠ WARNING: data.yaml not found at {yaml_path}")
    print("Please ensure your dataset has a data.yaml file in the root directory.")

# ==================== STEP 4: Create Symbolic Link ====================
print("\n" + "=" * 60)
print("STEP 4: Creating Symbolic Link")
print("=" * 60)

# Create symbolic link in the working directory for easier access
SYMLINK_PATH = '/content/beet_moth_data'

# Remove existing symlink if it exists
if os.path.islink(SYMLINK_PATH):
    os.unlink(SYMLINK_PATH)
elif os.path.exists(SYMLINK_PATH):
    import shutil
    shutil.rmtree(SYMLINK_PATH)

# Create new symbolic link
os.symlink(DRIVE_DATASET_PATH, SYMLINK_PATH)

print(f"✓ Created symbolic link: {SYMLINK_PATH} -> {DRIVE_DATASET_PATH}\n")

# ==================== STEP 5: Train YOLOv11 Model (v15 - Force Train) ====================
print("=" * 60)
print("STEP 5: Training YOLOv11 Nano Model - FORCE SESSION")
print("=" * 60)

from ultralytics import YOLO
import os

# 1. Define the PERMANENT path on your Google Drive
DRIVE_SAVE_PATH = '/content/drive/MyDrive/Euan_Work/BBRO/Data/AI_training/Beet_Moth_Project/runs'

# 2. Training parameters - UPDATED FOR V15
MODEL_NAME = 'yolo11n.pt'
EPOCHS = 100            # Increased to give the AI more time to learn
IMAGE_SIZE = 640
BATCH_SIZE = 16 
EXPERIMENT_NAME = 'beet_moth_v15' # New version name

print(f"""
Training Configuration:
  Model: {MODEL_NAME}
  Epochs: {EPOCHS}
  Image Size: {IMAGE_SIZE}
  Batch Size: {BATCH_SIZE}
  Dataset: {yaml_path}
  Project Path (Drive): {DRIVE_SAVE_PATH}
  Experiment: {EXPERIMENT_NAME}
""")

# Initialize model
print("Loading YOLOv11 nano model...")
model = YOLO(MODEL_NAME)

# Train the model
print("\n🚀 Starting V15 training (No Early Stopping)...\n")

results = model.train(
    data=yaml_path,
    epochs=EPOCHS,
    imgsz=IMAGE_SIZE,
    batch=BATCH_SIZE,
    project=DRIVE_SAVE_PATH,
    name=EXPERIMENT_NAME,
    device=0,
    patience=0,        # <--- CRITICAL: Forces the AI to finish all 100 epochs
    save=True,
    save_period=10,
    plots=True,
    verbose=True,
    lr0=0.01           # Start with a strong learning rate
)

print("\n✓ V15 Training completed and saved directly to Google Drive!\n")

# ==================== STEP 6: Save Best Model to Google Drive ====================
print("=" * 60)
print("STEP 6: Saving Best Model to Google Drive")
print("=" * 60)

import shutil
from datetime import datetime

# Find the best.pt file in the training results
RESULTS_PATH = f'{PROJECT_NAME}/{EXPERIMENT_NAME}'
BEST_MODEL_PATH = f'{RESULTS_PATH}/weights/best.pt'
LAST_MODEL_PATH = f'{RESULTS_PATH}/weights/last.pt'

# Create timestamped filename
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

if os.path.exists(BEST_MODEL_PATH):
    # Copy best model to Google Drive
    dest_best = os.path.join(DRIVE_MODELS_PATH, f'best_{timestamp}.pt')
    dest_best_latest = os.path.join(DRIVE_MODELS_PATH, 'best.pt')
    
    shutil.copy2(BEST_MODEL_PATH, dest_best)
    shutil.copy2(BEST_MODEL_PATH, dest_best_latest)
    
    print(f"✓ Best model saved to:")
    print(f"  - {dest_best}")
    print(f"  - {dest_best_latest}")
else:
    print(f"⚠ WARNING: best.pt not found at {BEST_MODEL_PATH}")

if os.path.exists(LAST_MODEL_PATH):
    # Also copy last model
    dest_last = os.path.join(DRIVE_MODELS_PATH, f'last_{timestamp}.pt')
    shutil.copy2(LAST_MODEL_PATH, dest_last)
    print(f"  - {dest_last}")

# Copy training results and plots
results_dest = os.path.join(DRIVE_MODELS_PATH, f'training_results_{timestamp}')
if os.path.exists(RESULTS_PATH):
    shutil.copytree(RESULTS_PATH, results_dest, dirs_exist_ok=True)
    print(f"\n✓ Training results saved to: {results_dest}")

# ==================== Summary ====================
print("\n" + "=" * 60)
print("TRAINING SUMMARY")
print("=" * 60)

print(f"""
Dataset: Beet Moth Detection
Model: YOLOv11 Nano
Epochs Trained: {EPOCHS}

Output Files in Google Drive:
  📁 Models Directory: {DRIVE_MODELS_PATH}
  🏆 Best Model: {DRIVE_MODELS_PATH}/best.pt
  📊 Full Results: {results_dest}

Next Steps:
  1. Review training plots in the results folder
  2. Test the model on validation/test images
  3. Use the best.pt model for inference

To run inference on new images:
  from ultralytics import YOLO
  model = YOLO('{DRIVE_MODELS_PATH}/best.pt')
  results = model('path/to/image.jpg')
""")

print("=" * 60)
print("✅ ALL DONE!")
print("=" * 60)



#New cell
# ==================== STEP 7: Test the Trained Model ====================



from ultralytics import YOLO
from google.colab.patches import cv2_imshow
import cv2

# 1. Load your 'Genius' from the new permanent path
model = YOLO('/content/drive/MyDrive/Euan_Work/BBRO/Data/AI_training/Beet_Moth_Project/models/beet_cop_V1.pt')

# 2. Run the test on a single image (quick test)
# This '.jpg' is being used as a test image
image_path = '/content/drive/MyDrive/Euan_Work/BBRO/Data/AI_training/Beet_Moth_Project/images/beet_moth_4156147703.jpg'
results = model.predict(source=image_path, conf=0.5)

# 3. Show the result immediately in Colab
for r in results:
    im_array = r.plot()  # This draws the boxes on the image
    cv2_imshow(im_array)