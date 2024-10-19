from process_image import ImageProcessor
import os
from PIL import Image, ImageDraw, ImageFont
from logger import info, error

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir
build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')

yolo_dir = "yolo_model/runs/detect/train/weights/best.pt"
yolo_path = os.path.join(root_directory, '..', 'build', yolo_dir)

def main():
    image_processor = ImageProcessor(yolo_path)

    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')  # Add more extensions if needed
    for label_name in os.listdir(arcface_dataset):
        label_path = os.path.join(arcface_dataset, label_name)
        if os.path.isdir(label_path):
            for image_name in os.listdir(label_path):
                image_path = os.path.join(label_path, image_name)
                if os.path.isfile(image_path) and image_path.lower().endswith(valid_extensions):
                    try:
                        image = Image.open(image_path)
                        result = image_processor.process_image(image)
                        info(f"Result: {result}")
                        
                        # Save the detected image with bounding boxes
                        save_detected_image(image, result['detections'], os.path.join(build_dir, 'output', image_name))
                    except Exception as e:
                        error(f"Error processing image {image_name}: {e}")

def save_detected_image(image, detections, output_path):
    # Ensure the image is in RGB mode
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    draw = ImageDraw.Draw(image)
    
    # Use the default font with the default size
    font = ImageFont.load_default()
    text_color = (0, 255, 0)  # Green color in RGB

    for detection in detections:
        bbox = detection['bbox']
        person_name = detection.get('person_name', 'Unknown')
        confidence = detection.get('confidence', 0)

        # Draw the bounding box and text
        draw.rectangle(bbox, outline='red', width=2)
        draw.text((bbox[0], bbox[1] - 10), f"{person_name} ({confidence:.2f})", fill=text_color, font=font)
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        image.save(output_path)
        info(f"Saved detected image to {output_path}")
    except Exception as e:
        error(f"Error saving image {output_path}: {e}")

if __name__ == '__main__':
    main()