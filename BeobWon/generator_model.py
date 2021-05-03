from __future__ import print_function, division
import scipy

import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.datasets import mnist
from tensorflow.keras import layers
from tensorflow.keras.layers import GaussianNoise
from tensorflow.keras.layers import Input, Dense, Reshape, Flatten, Dropout, Concatenate
from tensorflow.keras.layers import BatchNormalization, Activation, ZeroPadding2D
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.layers import UpSampling2D, Conv2D, Conv2DTranspose
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2
from tensorflow.keras.losses import binary_crossentropy
import datetime
import sys
import numpy as np
import os


def build_generator(g_power, img_shape):
    """U-Net Generator"""

    def conv2d_bn(x, filters, kernel_size, weight_decay=.0, strides=(1, 1)):
        layer = Conv2D(filters=filters,
                       kernel_size=kernel_size,
                       strides=strides,
                       padding='same',
                       use_bias=False,
                       kernel_regularizer=l2(weight_decay),
                       kernel_initializer='he_normal'
                       )(x)
        layer = BatchNormalization()(layer)
        return layer

    def conv2d_bn_relu(x, filters, kernel_size, weight_decay=.0, strides=(1, 1)):
        layer = conv2d_bn(x, filters, kernel_size, weight_decay, strides)
        layer = LeakyReLU(alpha=0.2)(layer)
        return layer

    def ResidualBlock(x, filters, kernel_size, weight_decay, downsample=True):
        if downsample:
            # residual_x = conv2d_bn_relu(x, filters, kernel_size=1, strides=2)
            residual_x = conv2d_bn(x, filters, kernel_size=1, strides=2)
            stride = 2
        else:
            residual_x = x
            stride = 1
        residual = conv2d_bn_relu(x,
                                  filters=filters,
                                  kernel_size=kernel_size,
                                  weight_decay=weight_decay,
                                  strides=stride,
                                  )
        residual = conv2d_bn(residual,
                             filters=filters,
                             kernel_size=kernel_size,
                             weight_decay=weight_decay,
                             strides=1,
                             )
        out = layers.add([residual_x, residual])
        out = LeakyReLU(alpha=0.2)(out)
        return out

    def ResidualBlockLast(x, filters, kernel_size, weight_decay, downsample=True):
        if downsample:
            # residual_x = conv2d_bn_relu(x, filters, kernel_size=1, strides=2)
            residual_x = conv2d_bn(x, filters, kernel_size=1, strides=2)
            stride = 2
        else:
            residual_x = conv2d_bn(x, filters, kernel_size=1, strides=1)
            stride = 1
        residual = conv2d_bn_relu(x,
                                  filters=filters,
                                  kernel_size=kernel_size,
                                  weight_decay=weight_decay,
                                  strides=stride,
                                  )
        residual = conv2d_bn(residual,
                             filters=filters,
                             kernel_size=kernel_size,
                             weight_decay=weight_decay,
                             strides=1,
                             )
        out = layers.add([residual_x, residual])
        out = LeakyReLU(alpha=0.2)(out)
        return out

    def deconv2d(layer_input, skip_input, filters, f_size=4, dropout_rate=0, upsampling=False):
        """Layers used during upsampling"""
        if upsampling:
            u = UpSampling2D(size=2)(layer_input)
        else:
            u = Conv2DTranspose(filters, kernel_size=f_size, strides=2,
                                padding='same', activation='relu')(layer_input)
        u = Conv2D(filters, kernel_size=f_size, strides=1,
                   padding='same', activation='relu')(u)
        if dropout_rate:
            u = Dropout(dropout_rate)(u)
        u = BatchNormalization(momentum=0.8)(u)
        u = Concatenate()([u, skip_input])
        #u = layers.add([u, skip_input])
        return u

    def deconv2d_same(layer_input, skip_input, filters, f_size=4, dropout_rate=0):
        """Layers used during upsampling"""
        u = Conv2D(filters, kernel_size=f_size, strides=1,
                   padding='same', activation='relu')(layer_input)
        if dropout_rate:
            u = Dropout(dropout_rate)(u)
        u = BatchNormalization(momentum=0.8)(u)
        u = Concatenate()([u, skip_input])
        #u = layers.add([u, skip_input])
        u = LeakyReLU(alpha=0.2)(u)
        return u

    # Image input
    d = Input(shape=img_shape)
    d0_0 = GaussianNoise(0.1)(d)

    d0_1 = conv2d_bn_relu(x=d0_0, filters=g_power, kernel_size=(
        4, 4), weight_decay=1e-4, strides=(1, 1))
    d0_2 = ResidualBlock(x=d0_1, filters=g_power, kernel_size=(
        4, 4), weight_decay=1e-4, downsample=False)
    # Downsampling
    d1_1 = ResidualBlock(x=d0_2, filters=g_power * 2,
                         kernel_size=(4, 4), weight_decay=1e-4, downsample=True)
    d1_2 = ResidualBlock(x=d1_1, filters=g_power * 2,
                         kernel_size=(4, 4), weight_decay=1e-4, downsample=False)
    d2_1 = ResidualBlock(x=d1_2, filters=g_power * 4,
                         kernel_size=(4, 4), weight_decay=1e-4, downsample=True)
    d2_2 = ResidualBlock(x=d2_1, filters=g_power * 4,
                         kernel_size=(4, 4), weight_decay=1e-4, downsample=False)
    d3_1 = ResidualBlock(x=d2_2, filters=g_power * 6,
                         kernel_size=(4, 4), weight_decay=1e-4, downsample=True)
    d3_2 = ResidualBlock(x=d3_1, filters=g_power * 6,
                         kernel_size=(4, 4), weight_decay=1e-4, downsample=False)

    # Upsampling
    u1_1 = deconv2d_same(d3_2, d3_1, g_power * 6)
    u1_2 = deconv2d(u1_1, d2_2, g_power * 4, upsampling=True)
    u2_1 = deconv2d_same(u1_2, d2_1, g_power * 4)
    u2_2 = deconv2d(u2_1, d1_2, g_power * 2)
    u3_1 = deconv2d_same(u2_2, d1_1, g_power * 2)
    u3_2 = deconv2d(u3_1, d0_2, g_power)
    u3_3 = deconv2d_same(u3_2, d0_1, g_power)

    output_img = ResidualBlockLast(x=u3_3, filters=4, kernel_size=(
        4, 4), weight_decay=1e-4, downsample=False)
    output_img = Conv2D(4, kernel_size=4, strides=1,
                        padding='same', activation='tanh')(output_img)

    return Model(d, output_img)
