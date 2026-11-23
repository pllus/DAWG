import os, time, json
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms

torch.backends.cudnn.benchmark = True
class config():
  ROOT_DIR = './'
  DATA_DIR = './data'
  LOG_NAME = 'resnet_w1a32'        # output folder name
  CIFAR = 10                       # 10 or 100
  WBITS = 1                        # weight bits (32 = full precision)
  ABITS = 32                       # activation bits (32 = full precision)
  LR = 0.1
  WD = 1e-4
  TRAIN_BATCH_SIZE = 128
  EVAL_BATCH_SIZE = 100
  MAX_EPOCHS = 60
  LOG_INTERVAL = 10
  NUM_WORKERS = 2
  PRETRAIN = False                 # set True to load PRETRAIN_DIR before training
  PRETRAIN_DIR = './ckpt/resnet20_baseline'

  LOG_DIR = os.path.join(ROOT_DIR, 'logs', LOG_NAME)
  CKPT_DIR = os.path.join(ROOT_DIR, 'ckpt', LOG_NAME)
  WEIGHT_DIR = os.path.join(ROOT_DIR, 'weights', LOG_NAME)
  for d in (DATA_DIR, LOG_DIR, CKPT_DIR, WEIGHT_DIR):
    os.makedirs(d, exist_ok=True)

  device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
  print('device:', device)