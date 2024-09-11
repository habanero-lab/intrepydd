#!/bin/bash

# lgc/install.sh

conda create -n lgc_env python=3.6 pip -y
source activate lgc_env

pip install numpy==1.16.3
pip install scipy==1.3.0
pip install pandas==0.24.2
pip install tqdm==4.32.1