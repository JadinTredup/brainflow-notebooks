# Windows Installation

## For use with Brainflow devices

#### 1. Install Miniconda
Go to this [link](https://docs.conda.io/en/latest/miniconda.html) to download and run the latest Python 3 miniconda 3 Windows 64-bit executable.

#### 2. Clone the github repo
* Open an Anaconda prompt and install git by running `conda install git`
* Navigate to you desired installation directory so as not to clone the repo directly to the home directory.
* Clone the repo with 
`git clone https:github.com/JadinTredup/brainflow-notebooks`
* Switch to the OpenBCI-NTX branch:  
```
cd brainflow-notebooks
git checkout remotes/origin/OpenBCI-NTX
```

#### 3. Create conda environment 
* Create conda environment `conda create -n"eeg-notebooks" python=3`.
* Activate the new environment `conda activate eeg-notebooks`.
* Install the necessary python dependencies  
```
pip install bitstring pylsl pygatt psychopy scikit-learn pandas numpy mne seaborn pyriemann pexpect jupyter brainflow pyglet muselsl git+https://github.com/peplin/pygatt
conda install -c conda-forge vispy
```

#### 4. Connect OpenBCI
* Plug in the USB dongle.
* **First time users:** If this is your first time connecting the OpenBCI board to your computer, you must first download and install the FTDI chip drivers [here](https://www.ftdichip.com/Drivers/VCP.htm).

#### 5. Test library
* In a conda terminal, activate the eeg-notebooks environment and navigate to the brainflow-notebooks directory.
* Start ipython `ipython`.
* Run the following to initiate a 20 second stimulus presentation after which, a file `first_test_run.csv` will be created in the current working directory.  
```python
import os

from eegnb import DATA_DIR, generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.experiment.visual_n170 import n170

# Session parameters
board_name = 'cyton'
port='COM5'       # Should be 'COM3' or 'COM5'
duration = 20
save_fn = os.path.abspath('first_test_run.csv')

# Set up EEG device
eeg_device = EEG(device=board_name, serial_port=port)

# Run experiment
n170.present(duration, eeg_device, save_fn)
```

#### 6. Generate experiment data
For accurate classification, at least 10 minutes of data per experiment should be run. The following script can be rerun multiple times to generate data for any experiment using any device.

```
from eegnb import DATA_DIR, generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.experiment.visual_n170 import n170

board_name = 'cyton'
subject_id = 'subject_name'
experiment = 'visual_n170'
port = 'COM5'      # Should be 'COM3' or 'COM5'

# Create the file name
save_fn = generate_save_fn(board_name, experiment, subject_id)

# Set up EEG device
eeg_device = EEG(device=board_name, serial_port=port)

# Run experiment
n170.present(duration, eeg_device, save_fn)
```
