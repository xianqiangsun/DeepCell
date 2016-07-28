'''Train a simple deep CNN on a HeLa dataset.
GPU run command:
    THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python cifar10_cnn.py

'''

from __future__ import print_function
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
# from keras.layers import Convolution2D, MaxPooling2D
# from keras.layers.normalization import BatchNormalization
from keras.optimizers import SGD, RMSprop
from keras.utils import np_utils
from CNN_layers import load_training_data, _residual_block, _bottleneck, _conv_bn_relu

from keras.models import Model
from keras.layers import (
    Input,
    Activation,
    merge,
    Dense,
    Flatten
)

from keras.layers.convolutional import Convolution2D, MaxPooling2D, AveragePooling2D

from keras.layers.normalization import BatchNormalization

batch_size = 32
nb_classes = 3
nb_epoch = 200
data_augmentation = True


training_data_file_name = '/home/vanvalen/ImageAnalysis/DeepCell/keras_version/training_data/HeLa_set1_61x61.npz'
file_name_save = '/home/vanvalen/ImageAnalysis/DeepCell/keras_version/trained_networks/'
(X_train, y_train), (X_test, y_test) =load_training_data(training_data_file_name)
# input image dimensions
img_rows, img_cols = 61, 61
img_channels = 2

# the data, shuffled and split between train and test sets
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
Y_train = np_utils.to_categorical(y_train, nb_classes)
Y_test = np_utils.to_categorical(y_test, nb_classes)

input = Input(shape = (2,61,61))

conv1 = _conv_bn_relu(nb_filter=64, nb_row=7, nb_col=7, subsample=(1, 1))(input)
pool1 = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), border_mode="same")(conv1)

# Build residual blocks..
block_fn = _bottleneck
block1 = _residual_block(block_fn, nb_filters=64, repetations=3, is_first_layer=True)(pool1)
block2 = _residual_block(block_fn, nb_filters=128, repetations=4)(block1)
block3 = _residual_block(block_fn, nb_filters=256, repetations=6)(block2)

# Classifier block
pool2 = AveragePooling2D(pool_size=(3, 3), strides=(1, 1), border_mode="valid")(block3)
flatten1 = Flatten()(pool2)
dense = Dense(output_dim=nb_classes, init="he_normal", activation="softmax")(flatten1)

model = Model(input=input, output=dense)


# let's train the model using SGD + momentum (how original).
sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
# rmsprop = RMSprop(lr = 0.001, rho = 0.95, epsilon = 1e-8)

model.compile(loss='categorical_crossentropy',
              optimizer=sgd,
              metrics=['accuracy'])

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
# X_train /= 255
# X_test /= 255

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(X_train, Y_train,
              batch_size=batch_size,
              nb_epoch=nb_epoch,
              validation_data=(X_test, Y_test),
              shuffle=True)
else:
    print('Using real-time data augmentation.')

    # this will do preprocessing and realtime data augmentation
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=180,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=True)  # randomly flip images

    # compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied)
    datagen.fit(X_train)

    # fit the model on the batches generated by datagen.flow()
    model.fit_generator(datagen.flow(X_train, Y_train,
                        batch_size=batch_size),
                        samples_per_epoch=X_train.shape[0],
                        nb_epoch=nb_epoch,
                        validation_data=(X_test, Y_test))

    model.save_weights(file_name_save)