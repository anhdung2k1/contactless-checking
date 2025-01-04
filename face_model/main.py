from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
from process_image import ImageProcessor
from s3_config.s3Config import S3Config
from logger import info, error
from argface_model.argface_classifier import ArcFaceClassifier
from facenet_model.facenet_model import FaceNetModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust allowed origins as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_location = os.path.abspath(__file__)
root_directory = os.path.dirname(file_location)
build_dir = os.path.join(root_directory, '..', 'build')

yolo_root_dir = os.path.join(build_dir, 'yolo_model')
yolo_dir = "yolo_model/train/weights/best.pt"
yolo_path = os.path.join(build_dir, yolo_dir)

# Export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION in your env
s3Config = S3Config()

if not os.path.exists(build_dir):
    info(f"Create {build_dir}")
    os.makedirs(build_dir)

if not os.path.exists(yolo_root_dir):
    info(f"Create {yolo_root_dir} folder")
    os.makedirs(yolo_root_dir)

if not os.path.exists(yolo_path):
    info(f"Create {yolo_path} folder")
    s3Config.download_all_objects('yolo_model/', build_dir)

# Initialize the ImageProcessor
image_processor = ImageProcessor(yolo_path)

@app.get("/health")
def health_check():
    try:
        return {"status": "ready", "message": "Service is healthy"}
    except Exception as e:
        error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
def upload_image(image: UploadFile = File(...)):
    try:
        info(f"File: {image.filename}")
        image_content = image.file.read()
        pil_image = Image.open(io.BytesIO(image_content))
        result = image_processor.process_image(pil_image)
        info(f"/upload: {result}")
        return result
    except Exception as e:
        error(f"Error in /upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@app.post("/retrieve")
def retrieve_image(image: UploadFile = File(...), customerName: str = Form(...)):
    try:
        info(f"File: {image.filename}\nCustomer Name: {customerName}")
        image_content = image.file.read()
        pil_image = Image.open(io.BytesIO(image_content))
        image_processor_with_name = ImageProcessor(yolo_path, customerName)
        result = image_processor_with_name.retrieve_image(pil_image)
        info(f"/retrieve: {result}")
        return result
    except Exception as e:
        error(f"Error in /retrieve: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve image: {str(e)}")

@app.post("/train")
def train_images(variableKey: list[str], variableValue: list[str]):
    arcface_dataset = os.path.join(build_dir, 'arcface_train_dataset')
    arcface_model_dir = os.path.join(build_dir, '.insightface')
    arcface_model_save = os.path.join(arcface_model_dir, 'arcface_model.pth')

    if not os.path.exists(arcface_dataset):
        error(f"{arcface_dataset} not found. Downloading from S3...")
        s3Config.download_all_objects('arcface_train_dataset/', build_dir)

    config = dict(zip(variableKey, variableValue))
    num_epochs = int(config.get("NUM_EPOCHS"))
    learning_rate = float(config.get("LEARNING_RATE"))
    momentum = float(config.get("MOMENTUM"))
    info(f"config: {config}")

    classifier = ArcFaceClassifier(arcface_dataset, arcface_model_dir, arcface_model_save)
    info("Initializing and training the model.")
    classifier.initialize_model()
    classifier.extract_features()
    classifier.train(num_epochs=num_epochs, lr=learning_rate, momentum=momentum)
    classifier.plot_training_metrics(os.path.join(arcface_model_dir, 'arcface_train_loss'))

    save_path = os.path.join(build_dir, 'face_net_train')
    model_file_path = os.path.join(save_path, 'facenet_model.pth')
    faceNetModel = FaceNetModel(
        image_path=arcface_dataset, batch_size=64, lr=learning_rate,
        num_epochs=num_epochs, save_path=save_path,
        model_file_path=model_file_path
    )
    faceNetModel.train()

    return {"status": "success", "message": "Model trained successfully"}

if __name__ == "__main__":
    import uvicorn

    tls_enabled = os.getenv("TLS_ENABLED", "false").lower() == "true"

    if tls_enabled:
        ca_path = os.getenv("CA_PATH")
        cert_path = os.getenv("CERT_PATH")
        key_path = os.getenv("KEY_PATH")
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5443,
            ssl_certfile=cert_path,
            ssl_keyfile=key_path,
            ssl_ca_certs=ca_path,
        )
    else:
        uvicorn.run(app, host="0.0.0.0", port=5000)
