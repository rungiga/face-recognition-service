import argparse
import requests
import glob

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", type=str, required=True,
	help="path to the input image folder")
args = vars(ap.parse_args())

images = glob.glob(args['input']+'/*')
labels = [' '.join(img.split('/')[-1].split('_')[:-1]) for img in images]


add_url = 'http://0.0.0.0:8080/api/face/create'
read_url = 'http://0.0.0.0:8080/api/face/read'

for img, lbl in zip(images, labels):
    files = {'image': open(img, 'rb')}
    payload = {'label': lbl}

    r = requests.post(add_url, params=payload, files=files)
    print(r.content.decode())

    r = requests.get(read_url, params=payload)
    print(r.content.decode())
