from flask import Flask
from flask_restful import Resource, Api, request
from flask_restful import reqparse
import numpy as np
from PIL import Image
import base64
import cv2
import sys

import tensorflow as tf

from BeobWon.predictCaptcha import PredictCaptcha as PredictBeobWonCaptcha
from MinWon24.predictCaptcha import PredictCaptcha as PredictMinWon24Captcha


app = Flask('innoCaptcha')
api = Api(app)


class CaptchaPredict(Resource):

    def __init__(self, gpu_on=True):
        if not gpu_on:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

        else:
            gpu_devices = tf.config.experimental.list_physical_devices('GPU')
            for device in gpu_devices:
                tf.config.experimental.set_memory_growth(device, True)

        self.request = request
        self.predictors = {}
        self.predictors['BeobWon'] = PredictBeobWonCaptcha()
        self.predictors['MinWon24'] = PredictMinWon24Captcha()

    def post(self):
        try:
            # convert string of image data to uint8
            img_array = np.frombuffer(
                base64.b64decode(self.request.data), dtype=np.uint8)
            # decode image
            img_array = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
            print(img_array.shape)
            # predict
            site = self.request.args.get('site')
            print(site)
            answer = self.predictors[site].predict(img_array)
            return {'answer': answer}
        except Exception as e:
            print(str(e))
            return {'error': str(e)}


api.add_resource(CaptchaPredict, '/predict')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
