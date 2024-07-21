from argface_model.argface_classifier import ArcFaceClassifier
import argparse
import os
from s3_config.s3Config import S3Config

file_location = os.path.abspath(__file__)  # Get current file abspath
root_directory = os.path.dirname(file_location)  # Get root dir

build_dir = os.path.join(root_directory, '..', 'build')
arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
arcface_model = os.path.join(build_dir, '.insightface')
arcface_dataset_test = os.path.join(build_dir, 'lfw_dataset', 'lfw')
# Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION in your env
s3Config = S3Config()

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
    parser.add_argument('--is_upload', action='store_true', help='Flag to upload to S3 bucket')
    parser.add_argument('--is_test', action='store_true', help='Flag to test the arcface model')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not args.is_test:
        if not os.path.exists(arcface_dataset):
            print(f"{arcface_dataset} not found. Downloading from S3...")
            s3Config.download_all_objects('arcface_train_dataset/', build_dir)
        
    # Initialize the classifier
    if not args.is_test:
        classifier = ArcFaceClassifier(arcface_dataset)
    else:
        classifier = ArcFaceClassifier(arcface_dataset_test)
    
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
        if args.is_upload:
            s3Config.upload_folder('.insightface', folder_path=arcface_model)
            print(f"Uploaded Model to S3 successfully")
        classifier.plot_training_metrics(os.path.join(arcface_model, 'arcface_train_loss'))
    elif args.mode == 'identify':
        if not args.image_path:
            raise ValueError("Image path is required for identification mode.")
        if not classifier.model_exists():
            raise FileNotFoundError("Model not found. Train the model first.")
        classifier.load_model()
        person_name = classifier.identify_person(args.image_path, args.save_image_path)
        print(f'The person in the image is: {person_name}')