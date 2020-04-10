# Brainflow Notebooks

This repository is a collection of EEG experiments which were originally developed by the [NeurotechX](https://neurotechx.com/) 
organization. The difference between this repository and the [original repository](https://github.com/neurotechx/eeg-notebooks) 
is that the notebooks have been edited to be compatible with the OpenBCI headset (specifically via the [brainflow API](https://brainflow.readthedocs.io/en/stable/#)).

## Getting Started

### Dependencies:
* Numpy, Matplotlib, Pandas, Seaborn
* Psychopy
* MNE
* Brainflow
* PyRiemann

#### Note for using Virtual Environments:  
If you are attempting to run these inside of a virtual environment, there can be some issues when attempting to install 
Psychopy. This is because PyQt5 takes some configuring to run inside of a venv. Instead of dealing with this headache, 
you can install PyQt5 on the system installation of Python3 then within in your virtual environment you can install
PyQt5 via the "vext" package by running: `pip install vext.pyqt5`. Because of this, you also need to install PsychoPy
and without dependencies and its other dependencies separately. In total you should run these three commands from within
your virtual environment:  
```
pip install vext.pyqt5

pip install arabic_reshaper astunparse distro esprima freetype-py future gevent \ 
    gitpython glfw imageio imageio-ffmpeg javascripthon json_tricks moviepy msgpack \
    msgpack-numpy opencv-python openpyxl pillow psutil pyglet pyopengl pyosf pyparallel \
    pyserial python-bidi python-gitlab pyyaml questplus requests[security] sounddevice \
    soundfile tables xlrd

pip install psychopy --no-deps
```

## Available Notebooks
* **Free Record**: This notebook is to allow you to freely record your own data for any duration for any desired task 
not included in the notebooks.
* **N170**:
* **P300**:
* **SSVEP**:

## Expanding the Repository

# Repository Status
The integration of the stimulus presentations with OpenBCI/Brainflow is work I have already completed and tested. This is 
just a porting and reformatting of that code to fit the NeurotechX EEG-Notebooks style. As such, I have yet to verify that
the experiments run 100% smoothly within the notebooks. I will work on verifying that within the coming days and will update
this section accordingly.

## General TO-DO:

1. **Combine data and events during stream:** as of right now the data and events are saved in separate files during recording and then segmented and lined up 
when loading the entire dataset. This can not be done in the same way as for the Muse because LSL is not beting used here.

## Notebook Statuses
* **N170**:  
    * *Stimulus Presentation*: **WORKING - 4/10/2020**
    * *Data Recording*: **WORKING - 4/10/2020**
    * *Visualization*:
    * *Classification Accuracy*: 
* **P300**:
    * *Stimulus Presentation*: **WORKING - 4/10/2020**
    * *Data Recording*: **WORKING - 4/10/2020**
    * *Visualization*:
    * *Classification Accuracy*:
* **SSVEP**: 
    * *Stimulus Presentation*: **WORKING - 4/10/2020**
    * *Data Recording*: **WORKING - 4/10/2020**
    * *Visualization*:
    * *Classification Accuracy*: