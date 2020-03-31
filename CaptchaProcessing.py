from flask import Flask
from flask_restful import Resource, Api, request
from flask_restful import reqparse
import numpy as np
import cv2
import sys

app = Flask('predict Captcha')
api = Api(app)
class CaptchaPredict(Resource) :
    
        def __init__(self, gpu_on = True) : 
            
            sys.path.insert(0, './법원')
            from predictCaptcha import PredictCaptcha
            self.predictor = PredictCaptcha()
            
            if not gpu_on :
                os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
                
        def post(self) :
            try :
                r = request
                # convert string of image data to uint8
                img_array = np.fromstring(r.data, np.uint8)
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
    
    
    
    
        click("123.png")