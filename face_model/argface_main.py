from argface_model.argface_classifier import ArcFaceClassifier
import argparse
import os

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')

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
    parser.add_argument('--mode', type=str, choices=['train', 'identify'], required=True, help='Mode: train or identify')
    parser.add_argument('--image_path', type=str, help='Path to the image for identification')
    parser.add_argument('--save_image_path', type=str, help='Path to save the identified image')
    parser.add_argument('--num_epochs', type=int, default=100, help='Number of epochs for training')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate for training')
    parser.add_argument('--momentum', type=float, default=0.9, help='Momentum for training')
    parser.add_argument('--continue_training', action='store_true', help='Flag to continue training from an existing model')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Initialize the classifier
    classifier = ArcFaceClassifier(arcface_dataset)

    if args.mode == 'train':
        if classifier.model_exists() and args.continue_training:
            print("Loading existing model and continuing training.")
            classifier.load_model()
            classifier.extract_features()
        else:
            print("Initializing and training the model.")
            classifier.initialize_model()
            classifier.extract_features()
        classifier.train(num_epochs=args.num_epochs, lr=args.learning_rate, momentum=args.momentum)
        print("Training completed.")
    elif args.mode == 'identify':
        if not args.image_path:
            raise ValueError("Image path is required for identification mode.")
        if not classifier.model_exists():
            raise FileNotFoundError("Model not found. Train the model first.")
        classifier.load_model()
        person_name = classifier.identify_person(args.image_path, args.save_image_path)
        print(f'The person in the image is: {person_name}')