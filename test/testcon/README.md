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
docker run -it --rm -v $PWD:$PWD:rw -w $PWD -p 5000:5000 anhdung12399/testcon:1.0.0 python face_model/main.py
```

To run `argface_main.py` locally to run train model.
```bash
docker run -it --rm -v $PWD:$PWD:rw -w $PWD anhdung12399/testcon:1.0.0 python face_model/argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9 --continue_training
```

### HOW TO USE MODEL TRAIN
To continue training existing model
```bash
$ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9 --continue_training
```
To train model
```bash
$ python argface_main.py --mode train --num_epochs 10000 --learning_rate 0.001 --momentum 0.9
```
To identify a person in a new image
```
$ python argface_main.py --mode identify --image_path /path/to/image.jpg --save_image_path /path/to/save_image.jpg
```
