Build testcon for create env for `face_model`. To save time for rebuild image.

1. Create image `testcon`
```
./vas.sh image_testcon
```
2. Upload `testcon` image to registry.
```
./vas.sh testcon_up
```

To run `face_model` locally to initial server session.
```bash
docker run -it --rm -v $PWD:$PWD:rw -w $PWD -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -p 5000:5000 anhdung12399/testcon:1.1.0 python face_model/main.py
```

To run `argface_main.py` locally to run train model. Parse the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY to environment.
```bash
docker run -it --rm -v $PWD:$PWD:rw -w $PWD -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY anhdung12399/testcon:1.1.0 python face_model/argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9 --continue_training --is_upload
```

### HOW TO USE MODEL TRAIN
To continue training existing model
```bash
$ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9 --continue_training --is_upload
```
To train model
```bash
$ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9
```
To save the model to S3
```bash
$ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9 --is_upload
```
To identify a person in a new image
```
$ python argface_main.py --mode identify --image_path /path/to/image.jpg --save_image_path /path/to/save_image.jpg
```
