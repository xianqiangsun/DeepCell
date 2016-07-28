'''Train a simple deep CNN on a HeLa dataset.
GPU run command:
	THEANO_FLAGS='mode=FAST_RUN,device=gpu,floatX=float32' python training_template.py

'''

from __future__ import print_function
from keras.optimizers import Adagrad

from cnn_functions import rate_scheduler, train_model_sample
from model_zoo import bn_feature_net_81x81 as the_model

import os
import datetime
import numpy as np

batch_size = 128
n_classes = 3
n_epoch = 50

model = the_model(n_channels = 2, n_features = 3, reg = 1e-5)
dataset = "HeLa_set1_81x81"
direc_save = "/home/nquach/DeepCell2/trained_networks/"
direc_data = "/home/nquach/DeepCell2/training_data_npz/"
optimizer = Adagrad(lr=0.01, epsilon=1e-08)
lr_sched = rate_scheduler(lr = 0.01, decay = 0.95)
expt = "bn81x81_adagrad"

iterate = 0
train_model_sample(model = model, dataset = dataset, optimizer = optimizer, 
	expt = expt, it = iterate, batch_size = batch_size, n_epoch = n_epoch,
	direc_save = "/home/nquach/DeepCell2/trained_networks/", 
	direc_data = "/home/nquach/DeepCell2/training_data_npz/", 
	lr_sched = lr_sched,
	rotate = True, flip = True, shear = 0)