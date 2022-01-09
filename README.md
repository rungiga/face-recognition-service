# Face Recognition Service

## Introduction
In this repository we will deploy a pretrained model for face detection purposes in two lightweight Docker containers.

## Installation
Please follow these steps for proper installation with the appropriate modifications:

* Clone this repository: `git clone https://github.com/gost-sniper/FD_Docker`
* Enter the local repo folder : `cd FD_Docker`
* Edit the docker-compose file with the appropriate hosts and ports
* Build and run the Docker image/container : `sudo docker-compose up --build -d`

Now we should have our model deployed at `0.0.0.0:8080` (or `localhost:8080` for windows users)

## Demo

### Create and Read

While the model is deployed you can use the `demo/create_and_read.py` to add a face to the database and then fetch its vector:

```
usage: create_and_read.py [-h] -i INPUT

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the input image folder
```
CLI :  `python3 demo/create_and_read.py -i path/to/folder`

### Search

While the model is deployed you can use the `demo/search.py` to search for a face to the database:



```
usage: search.py [-h] -i INPUT -c CONFIDENCE

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the input image folder
  -c CONFIDENCE, --confidence CONFIDENCE
                        confidence filter
```

CLI :  `python3 demo/search.py -i path/to/folder -c confidence/closness`


### Delete

To delete a list of label and their corespondent vectors use the `delete.py`:

```
usage: delete.py [-h] -i INPUT

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        path to the input image folder
```
CLI :  `python3 demo/delete.py -i path/to/folder`

## One image sample

To test this API with a simple images instead of folder of images use the `detect.py` file where you need to specify the action before the arguments:

```
usage: detect.py [-h] [--host HOST] [--port PORT] {create,read,search,delete} ...

positional arguments:
  {create,read,search,delete}

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           API Host
  --port PORT           API port
```


```shell
$ python3 demo/detect.py create --help
usage: detect.py create [-h] -i IMAGE -l LABEL

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        path to the input image
  -l LABEL, --label LABEL
                        Label of the input image


$ python3 demo/detect.py read --help
usage: detect.py read [-h] -l LABEL

optional arguments:
  -h, --help            show this help message and exit
  -l LABEL, --label LABEL
                        Label of the input image


$ python3 demo/detect.py search --help
usage: detect.py search [-h] -i IMAGE -c CONFIDENCE

optional arguments:
  -h, --help            show this help message and exit
  -i IMAGE, --image IMAGE
                        path to the input image
  -c CONFIDENCE, --confidence CONFIDENCE
                        Label of the input image


$ python3 demo/detect.py delete --help
usage: detect.py delete [-h] -l LABEL

optional arguments:
  -h, --help            show this help message and exit
  -l LABEL, --label LABEL
                        Label of the input image
```

CLI: 

create : `python3 demo/detect.py create -i path/to/image -l label`

read : `python3 demo/detect.py read -l label`

search : `python3 demo/detect.py search -i path/to/image -c confidence`

delete : `python3 demo/detect.py delete -l label`