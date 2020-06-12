from flask import Flask
from flask_restful import Resource, Api, request
from flask_restful import reqparse
import numpy as np
from PIL import Image
import base64
import cv2
import sys

# 사이트 늘어날 때 마다 추가
sys.path.insert(0, './법원')
sys.path.insert(0, './민원24')
from 법원.predict import PredictCaptcha
from predictCaptcha


app = Flask('predict Captcha')
api = Api(app)
class CaptchaPredict(Resource) :
    
        def __init__(self, gpu_on = True) : 
            #

            self.predictor = PredictCaptcha()
            self.r = request
            if not gpu_on :
                os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        def post(self) :
            try :
                # convert string of image data to uint8
                img_array = np.frombuffer(base64.b64decode(self.r.data), np.uint8)     
                # decode image
                img_array = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
                # predict
                answer = self.predictor.predict(img_array)      
                return {'answer' : answer}
            except Exception as e :
                return {'error' : str(e)}
            
api.add_resource(CaptchaPredict, '/predict') 


if __name__=='__main__' :
    app.run(debug = False, port = 5000)

