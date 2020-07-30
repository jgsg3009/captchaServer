from . generator_model import build_generator
from . solver_model import ResNet18_5_Parted_NoPooling as build_solver
import cv2
import os
import numpy as np
from time import time

class PredictCaptcha():
    def __init__(self) :
        
        currentPath = os.path.dirname(__file__)
        self.img_shape = (40,120,4)
        self.generator = build_generator(g_power = 25, img_shape = self.img_shape)
        self.solver = build_solver(input_shape=(40,120,4), size = 1, classes=10, weight_decay=5e-4)
        self.generator.load_weights(currentPath + '/generator_model_weights.h5')
        self.solver.load_weights(currentPath + '/solver_model_weights.h5')

    def predict(self, img_array) :
        
        # 각 사이트에 맞게 이미지 변형하기
        img_array = img_array[:,:,2]
        img_array = cv2.resize(img_array,(120,40))
        img_array[0,:] = 255
        img_array[-1,:] = 255
        img_array[:,0] = 255
        img_array[:,-1] = 255
        (thresh, img_array) = cv2.threshold(img_array, 127, 255, cv2.THRESH_TRUNC | cv2.THRESH_OTSU)
        img_array = img_array / thresh
        img_array = np.round(255*img_array).astype('uint8')
        img_array[img_array < np.mean(img_array)] = 0
        
        # 다운로드 - 캡쳐 이미지 불일치로 변환
        
        # GRAY => RGBA
        img_array = cv2.cvtColor(img_array,cv2.COLOR_GRAY2RGBA)
        
        # 사이트 공통 이미지 변형
        img_array = (img_array / 127.5) -1 
        img_array = np.array( [img_array,])
        converted_img = self.generator.predict(img_array)
        converted_img = np.round((converted_img+1)*127.5).astype('uint8')
        answer = self.solver.predict(converted_img)
        answer = list(map(lambda x : np.argmax(x), answer))
        answer = ''.join(map(str,answer))
        
        return answer
