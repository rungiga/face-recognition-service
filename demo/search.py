import argparse
import requests
import glob

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", type=str, required=True,
	help="path to the input image folder")
ap.add_argument("-c", "--confidence", type=float, required=True,
	help="confidence filter ")
args = vars(ap.parse_args())

images = glob.glob(args['input']+'/*')
labels = [' '.join(img.split('/')[-1].split('_')[:-1]) for img in images]


search_url = 'http://0.0.0.0:8080/api/face/search'

for img, lbl in zip(images, labels):
    files = {'image': open(img, 'rb')}
    payload = {"confidence": args['confidence']}
    r = requests.post(search_url, files=files, params=payload)
    print(r.json(), lbl)

