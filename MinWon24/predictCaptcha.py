from generator import build_generator
from solver import ResNet18_6_Parted_NoPooling as build_solver
import cv2
import numpy as np
from time import time

class PredictCaptcha():
    def __init__(self) :
        
        self.img_shape = (40,120,4)
        self.generator = build_generator(g_power = 50, img_shape = self.img_shape)
        self.solver = build_solver(input_shape=(40,120,4), size = 1, classes=10, weight_decay=5e-4)
        self.generator.load_weights('./법원/generator_weights.h5')
        self.solver.load_weights('./법원/solver_weights.h5')

    def predict(self, img_array) :
        
        img_array = (img_array / 127.5) -1 
        img_array = np.array( [img_array,])
        converted_img = self.generator.predict(img_array)
        converted_img = np.round((converted_img+1)*127.5).astype('uint8')
        answer = self.solver.predict(converted_img)
        answer = list(map(lambda x : np.argmax(x), answer))
        answer = ''.join(map(str,answer))
        
        return answer
