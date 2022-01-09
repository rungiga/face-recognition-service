import argparse
import requests
import json

parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="0.0.0.0",
	help="API Host")
parser.add_argument("--port", type=int, default=8080,
	help="API port")
subparsers = parser.add_subparsers(dest='subparser')
create_subparser = subparsers.add_parser('create')
create_subparser.add_argument("-i", "--image", type=str, required=True,
	help="path to the input image")
create_subparser.add_argument("-l", "--label", type=str, required=True,
	help="Label of the input image")

read_subparser = subparsers.add_parser('read')
read_subparser.add_argument("-l", "--label", type=str, required=True,
	help="Label of the input image")

search_subparser = subparsers.add_parser('search')
search_subparser.add_argument("-i", "--image", type=str, required=True,
	help="path to the input image")
search_subparser.add_argument("-c", "--confidence", type=float, required=True,
	help="Label of the input image")

delete_subparser = subparsers.add_parser('delete')
delete_subparser.add_argument("-l", "--label", type=str, required=True,
	help="Label of the input image")


args = vars(parser.parse_args())
HOST = args['host']
PORT = args['port']

if args['subparser'] == "create":
    add_url = f'http://{HOST}:{PORT}/api/face/create'

    files = {'image': open(args['image'], 'rb')}
    payload = {'label': args['label']}

    r = requests.post(add_url, params=payload, files=files)
    print(r.json())

elif args['subparser'] == "read":
    read_url = f'http://{HOST}:{PORT}/api/face/read'

    payload = {'label': args['label']}
    r = requests.get(read_url, params=payload)
    print(r.json())
elif args['subparser'] == "search":
    search_url = f'http://{HOST}:{PORT}/api/face/search'

    files = {'image': open(args['image'], 'rb')}
    payload = {"confidence": args['confidence']}
    r = requests.post(search_url, files=files, params=payload)
    print(json.dumps(r.json(), indent=4))

elif args['subparser'] == "delete":
    delete_url = f'http://{HOST}:{PORT}/api/face/delete'

    payload = {'label': args['label']}

    r = requests.delete(delete_url, params=payload)
    print(json.dumps(r.json(), indent=4))