from tensorflow.keras import layers
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import AveragePooling2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import MaxPool2D
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Activation
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras.regularizers import l2
import tensorflow as tf

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
    layer = Activation('relu')(layer)
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
    out = Activation('relu')(out)
    return out

def ResidualBlock_noPooling(x, filters, kernel_size, weight_decay):
    stride = 1
    residual_x = conv2d_bn(x, filters, kernel_size=kernel_size, strides=stride)
    
    
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
    out = Activation('relu')(out)
    return out

def ResNet18_6_Parted(classes, input_shape, weight_decay=1e-4):
    
    input = Input(shape=input_shape)
    x = input / 255
    # x = conv2d_bn_relu(x, filters=64, kernel_size=(7, 7), weight_decay=weight_decay, strides=(2, 2))
    # x = MaxPool2D(pool_size=(3, 3), strides=(2, 2),  padding='same')(x)
    x = conv2d_bn_relu(x, filters=64, kernel_size=(3, 3), weight_decay=weight_decay, strides=(1, 1))

    # # conv 2
    x = ResidualBlock(x, filters=64, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    x = ResidualBlock(x, filters=64, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    # # conv 3
    x = ResidualBlock(x, filters=128, kernel_size=(3, 3), weight_decay=weight_decay, downsample=True)
    x = ResidualBlock(x, filters=128, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    # # conv 4
    x = ResidualBlock(x, filters=256, kernel_size=(3, 3), weight_decay=weight_decay, downsample=True)
    x = ResidualBlock(x, filters=256, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    # # conv 5
    x = ResidualBlock(x, filters=512, kernel_size=(3, 3), weight_decay=weight_decay, downsample=True)
    x = ResidualBlock(x, filters=512, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    x = AveragePooling2D(pool_size=(5, 15), padding='valid')(x)
    x = Flatten()(x)
    x1 = Dense(classes, name = "digit1", activation='softmax',kernel_initializer='he_normal')(x)
    x2 = Dense(classes, name = "digit2", activation='softmax',kernel_initializer='he_normal')(x)
    x3 = Dense(classes, name = "digit3", activation='softmax',kernel_initializer='he_normal')(x)
    x4 = Dense(classes, name = "digit4", activation='softmax',kernel_initializer='he_normal')(x)
    x5 = Dense(classes, name = "digit5", activation='softmax',kernel_initializer='he_normal')(x)
    x6 = Dense(classes, name = "digit6", activation='softmax',kernel_initializer='he_normal')(x)
    
    model = Model(input, outputs = [x1,x2,x3,x4,x5,x6], name='ResNet18')
    return model

def ResNet18_6_Parted_NoPooling(classes, size, input_shape, weight_decay=1e-4):
    
    input = Input(shape=input_shape)
    x = input / 255
    # x = conv2d_bn_relu(x, filters=64, kernel_size=(7, 7), weight_decay=weight_decay, strides=(2, 2))
    # x = MaxPool2D(pool_size=(3, 3), strides=(2, 2),  padding='same')(x)
    x = conv2d_bn_relu(x, filters=8*size, kernel_size=(3, 3), weight_decay=weight_decay, strides=(1, 1))

    # # conv 2
    x = ResidualBlock(x, filters=8*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    x = ResidualBlock(x, filters=8*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    # # conv 3
    x = ResidualBlock(x, filters=16*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=True)
    x = ResidualBlock(x, filters=16*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    # # conv 4
    x = ResidualBlock(x, filters=32*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=True)
    x = ResidualBlock(x, filters=32*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    # # conv 5
    x = ResidualBlock(x, filters=64*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=True)
    x = ResidualBlock(x, filters=64*size, kernel_size=(3, 3), weight_decay=weight_decay, downsample=False)
    x = Flatten()(x)
    x1 = Dense(classes, name = "digit1", activation='softmax',kernel_initializer='he_normal')(x)
    x2 = Dense(classes, name = "digit2", activation='softmax',kernel_initializer='he_normal')(x)
    x3 = Dense(classes, name = "digit3", activation='softmax',kernel_initializer='he_normal')(x)
    x4 = Dense(classes, name = "digit4", activation='softmax',kernel_initializer='he_normal')(x)
    x5 = Dense(classes, name = "digit5", activation='softmax',kernel_initializer='he_normal')(x)
    x6 = Dense(classes, name = "digit6", activation='softmax',kernel_initializer='he_normal')(x)
    
    model = Model(input, outputs = [x1,x2,x3,x4,x5,x6], name='ResNet18')
    return model
