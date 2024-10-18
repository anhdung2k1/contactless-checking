from argface_model.argface_classifier import ArcFaceClassifier
import argparse
import os
from s3_config.s3Config import S3Config
from PIL import Image
import matplotlib.pyplot as plt
from logger import info, error

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model = os.path.join(build_dir, '.insightface')

##### HOW TO USE ####
# To continue training existing model
# $ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9 --continue_training
# To train model
# $ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9
# To identify a person in a new image
# $ python argface_main.py --mode identify --image_path /path/to/image.jpg --save_image_path /path/to/save_image.jpg
##################### 
def parse_arguments():
    parser = argparse.ArgumentParser(description='ArcFace Classifier')
    parser.add_argument('--mode', type=str, choices=['train', 'identify', 'identify_mul'], required=True, help='Mode: train, identify or identify mul')
    parser.add_argument('--image_path', type=str, help='Path to the image for identification')
    parser.add_argument('--folder_path', type=str, help='Path to the folder containing images for identification')
    parser.add_argument('--save_image_path', type=str, help='Path to save the identified image')
    parser.add_argument('--save_folder_path', type=str, help='Path to save the identified images')
    parser.add_argument('--num_epochs', type=int, default=100, help='Number of epochs for training')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate for training')
    parser.add_argument('--momentum', type=float, default=0.9, help='Momentum for training')
    parser.add_argument('--continue_training', action='store_true', help='Flag to continue training from an existing model')
    return parser.parse_args()

def save_image_with_label(image_path, label, save_path):
    image = Image.open(image_path)
    plt.figure()
    plt.imshow(image)
    plt.text(10, 10, label, fontsize=12, color='red', backgroundcolor='white')
    plt.axis('off')
    plt.savefig(save_path)
    plt.close()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not os.path.exists(arcface_dataset):
        # Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION in your env
        s3Config = S3Config()
        error(f"{arcface_dataset} not found. Downloading from S3...")
        s3Config.download_all_objects('arcface_train_dataset/', build_dir)
        
    # Initialize the classifier
    classifier = ArcFaceClassifier(arcface_dataset)
    
    if args.mode == 'train':
        if classifier.model_exists() and args.continue_training:
            info("Loading existing model and continuing training.")
            classifier.load_model()
            classifier.extract_features()
        else:
            info("Initializing and training the model.")
            classifier.initialize_model()
            classifier.extract_features()
        classifier.train(num_epochs=args.num_epochs, lr=args.learning_rate, momentum=args.momentum)
        info("Training completed.")
        classifier.plot_training_metrics(os.path.join(arcface_model, 'arcface_train_loss'))
    elif args.mode == 'identify':
        if not args.image_path:
            raise ValueError("Image path is required for identification mode.")
        if not classifier.model_exists():
            raise FileNotFoundError("Model not found. Train the model first.")
        classifier.load_model()
        person_name = classifier.identify_person(args.image_path)
        info(f'The person in the image is: {person_name}')

        if args.save_image_path:
            save_image_with_label(args.image_path, person_name, args.save_image_path)
            info(f"Identified image saved at {args.save_image_path}")
    elif args.mode == 'identify_mul':
        if not args.folder_path:
            raise ValueError("Folder path is required for identifying multiple images.")
        if not args.save_folder_path:
            raise ValueError("Save folder path is required for saving identified images.")
        if not classifier.model_exists():
            raise FileNotFoundError("Model not found. Train the model first.")
        classifier.load_model()

        # Process all images in the folder
        for image_name in os.listdir(args.folder_path):
            image_path = os.path.join(args.folder_path, image_name)
            if os.path.isfile(image_path):
                try:
                    person_name = classifier.identify_person(image_path)
                    save_path = os.path.join(args.save_folder_path, f"identified_{image_name}")
                    save_image_with_label(image_path, person_name, save_path)
                    info(f'Identified {person_name} in {image_name} and saved to {save_path}')
                except Exception as e:
                    error(f"Error identifying person in image {image_name}: {e}")
