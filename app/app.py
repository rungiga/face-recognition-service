import logging
import os

import dlib
import face_recognition
import postgresql

from flask import Flask, jsonify, make_response
from flask_restx import Api, Resource

import numpy as np
import cv2
import ast

from werkzeug.datastructures import FileStorage

DB_HOST = os.environ.get('DB_HOST', "localhost")
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_USER = os.environ.get('DB_USER', "user")
DB_PASSWORD = os.environ.get('DB_PASSWORD', "user")
DB_NAME = os.environ.get('DB_NAME', 'db')
DEBUG = os.environ.get('DEBUG', False)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
api = Api(app, doc='/docs', version='1.0',
          title=' Wrapper for a Published Object-Detection Model',
          description='Object Detection API')
# Create a HOG face detector using the built-in dlib class
face_detector = dlib.get_frontal_face_detector()

add_parser = api.parser()
add_parser.add_argument('image', location='files',
                        type=FileStorage, required=True)
add_parser.add_argument('label', type=str, required=True)

read_parser = api.parser()
read_parser.add_argument('label', type=str, required=True)

search_parser = api.parser()
search_parser.add_argument('image', location='files',
                           type=FileStorage, required=True)
search_parser.add_argument('confidence', type=float, required=True)

db_url = f'pq://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
logging.debug(db_url)

logging.info('Initialize DB')
db = postgresql.open(db_url)

db.execute("create extension if not exists cube;")
db.execute("drop table if exists vectors")
db.execute("create table vectors (id serial, label varchar, vec_low cube, vec_high cube);")
db.execute("create index vectors_vec_idx on vectors (vec_low, vec_high);")

logging.info('DB Initialized')


@api.route('/api/face/create', doc={
    "description": "Add a face to the database",
})
@api.expect(add_parser)
class Add(Resource):
    @api.response(200, 'Success')
    @api.response(501, 'Invalid file format')
    @api.response(502, 'Face does not exist')
    @api.response(503, 'Multiple Face in the picture')
    @api.response(504, 'Face label already exists')
    def post(self):
        args = add_parser.parse_args()
        label = args['label']
        query = f""" SELECT label FROM vectors WHERE label = '{label}' """
        res = db.prepare(query).first()

        if res is not None:
            return "Face label {} already existant".format(label), 504
        added_file = args['image'].read()
        # convert string data to numpy array
        npimg = np.fromstring(added_file, np.uint8)
        # convert numpy array to image
        image = cv2.imdecode(npimg, cv2.cv2.IMREAD_COLOR)

        if image is None:
            return 'Invalid file format', 501

        # Run the HOG face detector on the image data
        detected_faces = face_detector(image, 1)
        if len(detected_faces) == 0:
            return "0 face were found in the picture", 502
        elif len(detected_faces) > 1:
            return "Multiple faces in the picture", 503
        else:
            for i, face_rect in enumerate(detected_faces):
                # Detected faces are returned as an object with the coordinates
                # of the top, left, right and bottom edges
                logging.info("- Face #{} found at Left: {} Top: {} Right: {} Bottom: {}".format(i, face_rect.left(),
                                                                                                face_rect.top(),
                                                                                                face_rect.right(),
                                                                                                face_rect.bottom()))
                crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
                encodings = face_recognition.face_encodings(crop)

                if len(encodings) > 0:
                    query = "INSERT INTO vectors (label, vec_low, vec_high) " \
                            "VALUES ('{}', CUBE(array[{}]), CUBE(array[{}]))".format(label,
                                                                                     ','.join(str(s) for s in
                                                                                              encodings[0][:64]),
                                                                                     ','.join(str(s) for s in
                                                                                              encodings[0][64:128]))

                    db.execute(query)

                    # cv2.imwrite("./.faces/aligned_face_{}_{}_crop.jpg".format(file_name.replace('/', '_'), i), crop)
            return "Success, Image added for {}".format(label), 200


@api.route('/api/face/read', doc={
    "description": "Get a vector face",
})
@api.expect(read_parser)
class Read(Resource):
    @api.response(200, 'Succes')
    @api.response(404, 'Label inexistant')
    def get(self):
        args = read_parser.parse_args()
        label = args['label']
        query = f""" SELECT vec_low, vec_high FROM vectors WHERE label = '{label}' """
        res = db.prepare(query).first()
        if res is None:
            return f"Missing the label '{label}' from the database", 404
        else:
            return make_response(jsonify(dict([(k, ast.literal_eval(v)) for k, v in res.items()])), 200)


@api.route('/api/face/delete', doc={
    "description": "Delete a label from the database",
})
@api.expect(read_parser)
class Remove(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Label does not exist')
    def delete(self):
        args = read_parser.parse_args()
        label = args['label']
        query = f""" SELECT vec_low, vec_high FROM vectors WHERE label = '{label}' """
        res = db.prepare(query).first()
        if res is None:
            return f"Missing the label '{label}' from the database", 404

        query = f""" DELETE FROM vectors WHERE label = '{label}' """
        a = db.prepare(query)
        a()

        return f"Deleted succesfully the label {label}", 200


@api.route('/api/face/search', doc={
    "description": "Add a face to the database",
})
@api.expect(search_parser)
class Search(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'No faces in the picture')
    @api.response(501, 'Invalid file format')
    @api.response(502, 'Face does not exist')
    @api.response(503, 'Multiple Face in the picture')
    @api.response(504, 'Face label already exists')
    def post(self):
        args = search_parser.parse_args()
        threshold = args['confidence']

        added_file = args['image'].read()
        # convert string data to numpy array
        npimg = np.fromstring(added_file, np.uint8)
        # convert numpy array to image
        image = cv2.imdecode(npimg, cv2.cv2.IMREAD_COLOR)

        if image is None:
            return 'Invalid file format', 501

        # Run the HOG face detector on the image data
        detected_faces = face_detector(image, 1)

        if len(detected_faces) <= 0:
            return "No face detected in the photo", 404
        results = []
        # Loop through each face we found in the image
        for face_rect in detected_faces:
            crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]

            encodings = face_recognition.face_encodings(crop)
            if len(encodings) > 0:
                low = ','.join(str(s) for s in encodings[0][:64])
                high = ','.join(str(s) for s in encodings[0][64:128])
                query = "SELECT label, " \
                        "sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) " \
                        "AS score " \
                        "FROM vectors " \
                        "WHERE sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) <= {} " \
                        "ORDER BY sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) " \
                        "ASC LIMIT 1".format(
                    low,
                    high,
                    low,
                    high,
                    threshold,
                    low,
                    high,
                )

                res = db.prepare(query).first()
                if res:
                    results.append({
                        "label": res['label'],
                        "score": res['score'],
                        "box": {
                            "Left": face_rect.left(),
                            "Top": face_rect.top(),
                            "Right": face_rect.right(),
                            "Bottom": face_rect.bottom()
                        }
                    })
                else:
                    results.append({
                        "label": "UNKNOWN",
                        "score": 1000,
                        "box": {
                            "Left": face_rect.left(),
                            "Top": face_rect.top(),
                            "Right": face_rect.right(),
                            "Bottom": face_rect.bottom()
                        }
                    })

        return make_response(jsonify(results), 200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=DEBUG)
