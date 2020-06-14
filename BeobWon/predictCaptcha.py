from generator import build_generator
from solver import ResNet18_6_Parted_NoPooling as build_solver
import cv2
import numpy as np
from time import time

class PredictCaptcha():
    def __init__(self) :
        
        # GAN input_shape = (40,120,3)
        # Solver input_shape = (40,120,4)
        self.img_shape = (40,120,3)
        self.generator = build_generator(g_power = 50, img_shape = self.img_shape)
        self.solver = build_solver(input_shape=(40,120,4), size = 1, classes=10, weight_decay=5e-4)
        self.generator.load_weights('./BeobWon/generator_weights.h5')
        self.solver.load_weights('./BeobWon/solver_weights.h5')

    def predict(self, img_array) :
        
        # 다운로드 - 캡쳐 이미지 불일치로 변환
        img_shape = img_array.shape
        new_img = np.zeros(img_shape, np.uint8)
        for i in range(img_shape[0]) :
            for j in range(img_shape[1]) :
                for channel in range(img_shape[2]) :
                        new_img[i,j,channel] = 255 - img_array[i,j,channel] 
        img_array = new_img
        
        # 각 사이트에 맞게 이미지 변형하기
        
        # 사이트 공통 이미지 변형 
        img_array = (img_array / 127.5) -1 
        img_array = np.array( [img_array,])
        converted_img = self.generator.predict(img_array)
        converted_img = np.round((converted_img+1)*127.5).astype('uint8')
        # 정답 구하기
        answer = self.solver.predict(converted_img)
        answer = list(map(lambda x : np.argmax(x), answer))
        answer = ''.join(map(str,answer))
        
        return answer
