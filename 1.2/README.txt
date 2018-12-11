########## 必要なpython module  ################
#DSO-X4024A
from PyQt5 import QtCore, QtGui, QtWidgets
### additional modules ###
import subprocess
import time
from datetime import datetime
from matplotlib import pyplot as plt
import sys
import os
import numpy as np
import pandas as pd
import random
import glob
import scipy.fftpack as sf
import scipy as sp
 
rubyも必要。
 
########## インストール方法################
tar -xvf nspec.tar.gz
########## Hardware setup ################
KEYSIGHT DSOX4024A  - ethernetHUB – PC
の形でLANで接続する。
使用するパソコンからオシロのIPアドレスが見えるようにする。
Python
Import visa
rm = visa.ResourceManager()
rm.list_resources()
でオシロが見えていることを確認しておく。
########## 使い方################
./nspec.py
 
“Configuration”… 機器への接続
GUIの“Configuration”からIPアドレスをformに手入力する。
“connect”ボタンをおす。接続できたら機器情報が取得される。
 
Scope Setup … 初期設定または測定条件ファイルの読み込み
“Scope Setup”から、”select”ボタンをおす。
./commフォルダ以下にある”setup_initialize.txt”を開く。
必要に応じてファイルを編集した場合は、”save”ボタンを押して保存する。
“send Command”ボタンを押すと実行され初期設定される。
 
“Nspec”… データの取得からプロットまで。
“Nspec”から取得したい周波数帯域にチェックを入れる。
（独自に設定した測定条件ファイルの元でノイズスペクトルを取得したい場合には、“Scope Setup”でファイルを実行してから、Manualにチェックを入れる。）
“start”ボタンを押すと、オシロからデータを取得してFFTをかけてプロットまでしてくれる。
 
正しい測定条件ファイルは、まだ無いので準備する必要があります。

########## update ver 1.2 ################
11/13/2018 by Akio Hoshino
1. ./nspec.pyに send_commandを追加してコマンド１行でも送れるように改善した。
2.  queryのreturnを得たい場合にも対応しているので、気にせずコマンドを送信できる。
3. :WAVEFORM:PREAMBLE?の結果をread_preambleで読み出してnoise tab上で表示する。
