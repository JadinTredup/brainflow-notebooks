# Brainflow Notebooks

***NOTE :* This repository has been deprecated. Brainflow notebooks has been integrated into the original EEG notebooks where other developers and myself are consistently updating: ([Github Repo](https://github.com/neurotechx/eeg-notebooks)) ([Documentation](https://neurotechx.github.io/eeg-notebooks/))**

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

## Using the Notebooks
The notebooks rely on backend classes that are contained in the `experiments.py` and the `dataset.py` files. To describe 
how the API works, we will break the notebooks into two parts: data collection and data analysis.

### Data Collection
Running the data collection has 3 steps:
1. Setting up the correct stimulus presentation for the desired paradigm.
2. Initialize the EEG device.
3. Run the trial(s).

#### 1. Setting up the experiment
The different types of experiments can all be imported in from the `experiments.py` file. At the moment there are only two paradigms
available: ERPs and SSVEP. Different experiments can be loaded with the following commands:
```python
from experiments import eventRelatedPotential, steadyStateEvokedPotentials

# SSVEP experiment:
ssvep_exp = steadyStateEvokedPotentials()

# ERP, using the N170 stimuli:
n170_exp = eventRelatedPotential(erp='n170')

# ERP, using the P300 stimuli:
p300_exp = eventRelatedPotential(erp='p300')
```

#### 2. Initialize the EEG device
As of right now, brainflow supports both the OpenBCI and BrainBit headsets, and there is also a synthetic data source within
the API itself. The notebooks at the moment only support the OpenBCI and synthetic headsets, but adding the additional setups as they
come will be easy enough by adding a few lines of code. To initialize the devices:
```python
# For the synthetic board
exp.initialize_eeg(board_type='synthetic')

# For the Ganglion board:
exp.initialize_eeg(board_type='ganglion')           # Using USB
exp.initialize_eeg(board_type='ganglion_wifi')      # Using Wifi

# For using the 8-channel Cyton board
exp.initialize_eeg(board_type='cyton')              # Using USB
exp.initialize_eeg(board_type='cyton_wifi')         # Using Wifi

# For using the 16-channel Cyton+Daisy combo
exp.initialize_eeg(board_type='cyton_daisy')        # Using USB
exp.initialize_eeg(board_type='cyton_daisy_wifi')   # Using Wifi

# For using the BrainBit headband:
exp.initialize_eeg(board_type='brainbit')

# For using the Unicorn device
exp.initialize_eeg(board_type='unicorn')
```

#### 3. Run data collection
Now to run the experiment, you must define a subject name, trial duration, and trial number. The subject name and trial 
number will be used in the save file name for easy access later. **Note:** This portion of the code should always be run 
in a separate notebook cell. It is set up so that the cell can be repeated over and over again without needing to repeat 
the previous two steps. It is just recommended to increment the trial number with each pass, and change the subject name 
accordingly.
```python
subject_name = 'test_subject'
duration = 60
trial_num = 3
exp.run_trial(duration=duration,
              subject=subject_name,
              run=trial_num)
```

#### Full example
Now putting it all together, if we wanted to run the N170 experiment for a 16-channel configuration, we would need in two 
separate notebook cells:
```python
from experiments import eventRelatedPotential, steadyStateEvokedPotentials

n170_exp = eventRelatedPotential(erp='n170')
n170_exp.initialize_eeg(board_type='daisy')
```
In a separate cell:
```python
subject_name = 'test_subject'
duration = 60
trial_num = 3
n170_exp.run_trial(duration=duration,
                   subject=subject_name,
                   run=trial_num)
```

### Data Analysis
As EEG data analysis differs from paradigm to paradigm, this portion will really only cover the `dataset.py` module. This 
module loads the data and event files saved by the experiment and combines them into a single object. Brainflow offers some
filtering and pre-processing functions which will be detailed/utilized in later notebooks, but right now the best practice is
to use this module to output the unfiltered data as an MNE Raw object and perform filtering within MNE. To do this, you must 
define the subject and run numbers for which you want to load the data, the paradigm recorded, and the board type. There is an optional 
`layout` parameter which can be used for passing nonstandard arrangements of channel names for the OpenBCI headsets. After 
loading the dataset, you can convert it to a raw type, only selecting the runs you wish to keep.

```python
subject_name = 'synthetic_test'
runs = [0, 1, 2]
dataset_n170 = branflowDatasety(paradigm='n170',
                                subject=subject_name,
                                board_type='synthetic')   
raw = dataset_n170.load_subject_to_raw(subject_name, runs)
```


## Available Notebooks
* **Free Record**: This notebook is to allow you to freely record your own data for any duration for any desired task 
not included in the notebooks.
* **N170**:
* **P300**:
* **SSVEP**:

## Initializing the Boards
Each board has optional parameters that can be passed to the `exp.initialize_eeg()` method. 

**OpenBCI:**
For the OpenBCI boards, there is an option to pass the USB port needed for the dongle, but there is a default port for 
both Linux and Windows so it is optional on those two operating systems. The Ganglion however, also needs a layout of EEG 
electrode locations passed to it, as there is not a standardized 4-channel configuration. Additionally, if using the Wifi 
shield in *DIRECT* mode, the API uses a default IP address and finds an open port. If ot using in direct mode, you must pass
the ip address of the board to the `ip_addr` parameter.

**BrainBit and Unicorn:** BrainBit and Unicorn both have the option of passing their serial numbers to the `serial_num` 
parameter. This makes it possible to connect multiple headsets at the same time.



# Repository Status
The integration of the stimulus presentations with OpenBCI/Brainflow is work I have already completed and tested. This is 
just a porting and reformatting of that code to fit the NeurotechX EEG-Notebooks style. As such, I have yet to verify that
the experiments run 100% smoothly within the notebooks. I will work on verifying that within the coming days and will update
this section accordingly.

## Supported Board Status
Here is a list of all of the boards brainFlow supports and their status of being integrated into the notebooks:

**OpenBCI Ganglion:**
- [X] Added
- [ ] Connection tested
- [ ] Recording tested
- [ ] Data loading tested

**OpenBCI Cyton:**
- [X] Added
- [X] Connection tested
- [X] Recording tested
- [X] Data loading tested

**OpenBCI Cyton and Daisy:**
- [X] Added
- [X] Connection tested
- [X] Recording tested
- [X] Data loading tested

**OpenBCI Wifi:**
- [X] Added
- [ ] Connection tested
- [ ] Recording tested
- [ ] Data loading tested

**NeuroMD BrainBit:**
- [X] Added
- [ ] Connection tested
- [ ] Recording tested
- [ ] Data loading tested

**G.TEC Unicorn:**
- [X] Added
- [ ] Connection tested
- [ ] Recording tested
- [ ] Data loading tested

## General TO-DO:

- [ ] **Combine data and events during stream:** as of right now the data and events are saved in separate files during recording and then segmented and lined up 
when loading the entire dataset. This can not be done in the same way as for the Muse because LSL is not beting used here.
- [X] **Add support for BrainBit:** Add the necessary lines to functions in both `experiments.py` and `dataset.py` to 
accommodate the BrainBit headset. 

## Notebook Statuses
* **N170**:  
    - [X] *Stimulus Presentation*: **WORKING - 4/10/2020**
    - [X] *Data Recording*: **WORKING - 4/10/2020**
    - [ ] *Visualization*:
    - [X] *Classification Accuracy*: **WORKING - 4/10/2020**
* **P300**:
    - [X] *Stimulus Presentation*: **WORKING - 4/10/2020**
    - [X] *Data Recording*: **WORKING - 4/10/2020**
    - [ ] *Visualization*:
    - [ ] *Classification Accuracy*:
* **SSVEP**: 
    - [X] *Stimulus Presentation*: **WORKING - 4/10/2020**
    - [X] *Data Recording*: **WORKING - 4/16/2020**
    - [X] *Visualization*: **WORKING - 4/24/2020**
    - [ ] *Classification Accuracy*:
