import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

try:
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
except ImportError:
    print("Okk")

# Function to check image file extensions
def check_image_extensions(directory, allowed_extensions=['.jpg', '.jpeg', '.png']):
    for root, _, files in os.walk(directory):
        for file in files:
            if not file.lower().endswith(tuple(allowed_extensions)):
                print(f"Incorrect file format: {file}")


# Function to check image shape and channels
def check_image_shape(directory, target_size=(224, 224), channels=3):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with Image.open(file_path) as img:
                    if img.size != target_size or (img.mode != 'RGB' and channels == 3):
                        print(f"Image {file_path} has incorrect dimensions or color channels: {img.size}, {img.mode}")
            except Exception as e:
                print(f"Error loading image {file_path}: {e}")


# Function to check for corrupt images
def check_for_corrupt_images(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with Image.open(file_path) as img:
                    img.verify()  # This checks if the image is corrupted
            except (IOError, SyntaxError) as e:
                print(f"Corrupt image found: {file_path}, Error: {e}")


# Function to check the output of the ImageDataGenerator
def check_image_generator_output(generator):
    batch = next(generator)
    print("Batch shape:", batch[0].shape)
    print("Batch labels shape:", batch[1].shape)

    # Display the first image in the batch
    plt.imshow(np.uint8(batch[0][0] * 255))
    plt.show()


# Directories for training and validation data
train_dir = 'D:\\Data\\Environment\\trainingData'
val_dir = 'D:\\Data\\Environment\\valData'

# Run the checks
print("Checking image extensions...")
check_image_extensions(train_dir)
check_image_extensions(val_dir)

print("\nChecking image shapes and channels...")
check_image_shape(train_dir)
check_image_shape(val_dir)

print("\nChecking for corrupt images...")
check_for_corrupt_images(train_dir)
check_for_corrupt_images(val_dir)

# Assuming you have already defined your ImageDataGenerator and generators
# Replace these with your actual generator definitions if needed
train_datagen = ImageDataGenerator(rescale=1. / 255)
train_generator = train_datagen.flow_from_directory(train_dir, target_size=(224, 224), batch_size=32,
                                                    class_mode='categorical')

print("\nChecking ImageDataGenerator output...")
check_image_generator_output(train_generator)
