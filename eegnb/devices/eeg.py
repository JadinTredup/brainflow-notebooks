""" Abstraction for the various supported EEG devices.

    1. Determine which backend to use for the board.
    2.

"""
from time import sleep

import numpy as np
import pandas as pd

from brainflow import DataFilter, BoardShim, BoardIds, BrainFlowInputParams

from eegnb.devices.utils import get_openbci_usb, get_openbci_ip, BRAINFLOW_CHANNELS, create_stim_array

brainflow_devices = [
    'ganglion', 'ganglion_wifi',
    'cyton', 'cyton_wifi',
    'cyton_daisy', 'cyton_daisy_wifi',
    'brainbit', 'unicorn', 'synthetic'
]

class EEG:

    def __init__(self, device=None):
        '''
        Parameters:
            device (str): name of eeg device used for reading data.
        '''
        # determine if board uses brainflow or muselsl backend
        self.device_name = device
        self.backend = self._get_backend(self.device_name)
        self.initialize_backend()

    def initialize_backend(self):
        if self.backend == 'brainflow':
            self._init_brainflow()
        #else:
            #self._init_muselsl()

    def _get_backend(self, device_name):
        if (device_name in brainflow_devices):
            return 'brainflow'
        else:
            return 'muse'

    #####################
    #   MUSE functions  #
    #####################
    #def _init_muselsl(self):
    #def _start_muse(self):
    #def _stop_muse(self):
    #def _muse_push_sample(self):

    ##########################
    #   BrainFlow functions  #
    ##########################
    def _init_brainflow(self, serial_num=None):
        # Initialize brainflow parameters
        self.brainflow_params = BrainFlowInputParams()
        if self.device_name == 'ganglion':
            self.brainflow_id = BoardIds.GANGLION_BOARD.value
            self.brainflow_params.serial_port = get_openbci_usb()

        elif self.device_name == 'ganglion_wifi':
            brainflow_id = BoardIds.GANGLION_WIFI_BOARD.value
            self.brainflow_params.ip_address, self.brainflow_params.ip_port = get_openbci_ip()

        elif self.device_name == 'cyton':
            self.brainflow_id = BoardIds.CYTON_BOARD.value
            self.brainflow_params.serial_port = get_openbci_usb()

        elif self.device_name == 'cyton_wifi':
            self.brainflow_id = BoardIds.CYTON_WIFI_BOARD.value
            self.brainflow_params.ip_address, self.brainflow_params.ip_port = get_openbci_ip()

        elif self.device_name == 'cyton_daisy':
            self.brainflow_id = BoardIds.CYTON_DAISY_BOARD.value
            self.brainflow_params.serial_port = get_openbci_usb()

        elif self.device_name == 'cyton_daisy_wifi':
            self.brainflow_id = BoardIds.CYTON_DAISY_WIFI_BOARD.value
            self.brainflow_params.ip_address, self.brainflow_params.ip_port = get_openbci_ip()

        elif self.device_name == 'brainbit':
            self.brainflow_id = BoardIds.BRAINBIT_BOARD.value
            if serial_num:
                self.brainflow_params.other_info = serial_num

        elif self.device_name == 'unicorn':
            self.brainflow_id = BoardIds.UNICORN_BOARD.value
            if serial_num:
                self.brainflow_params.other_info = serial_num

        elif self.device_name == 'synthetic':
            self.brainflow_id = BoardIds.SYNTHETIC_BOARD.value

        # Initialize board_shim
        self.sfreq = BoardShim.get_sampling_rate(self.brainflow_id)
        self.board = BoardShim(self.brainflow_id, self.brainflow_params)
        self.board.prepare_session()

    def _start_brainflow(self):
        self.board.start_stream()
        # wait for signal to settle
        sleep(5)

    def _stop_brainflow(self):
        data = self.board.get_board_data()
        data = data.T
        ch_names = BRAINFLOW_CHANNELS[self.device_name]
        num_channels = len(ch_names)
        eeg_data = data[:, 1:num_channels+1]
        timestamps = data[:, -1]
        stim_array = create_stim_array(timestamps, self.markers)
        timestamps = timestamps[..., None]
        total_data = np.append(timestamps, eeg_data, 1)
        total_data = np.append(total_data, stim_array, 1)
        # Subtract five seconds of settling time from beginning
        total_data = total_data[5*self.sfreq:]
        data_df = pd.DataFrame(total_data, columns=['timestamps'] + ch_names + ['stim'])
        data_df.to_csv(self.save_fn)

    def _brainflow_push_sample(self, marker):
        last_timestamp = self.board.get_current_board_data(1)[-1][0]
        self.markers.append([marker, last_timestamp])

    def start(self, fn):
        self.save_fn = fn
        if self.backend == 'brainflow':
            self._start_brainflow()
            self.markers = []
        #elif self.backend == 'muselsl':
            #self._start_muse()

    def push_sample(self, marker, timestamp):
        if self.backend == 'brainflow':
            self._brainflow_push_sample(marker=marker)
        #elif self.backend == 'muselsl':

    def stop(self):
        if self.backend == 'brainflow':
            self._stop_brainflow()
        #elif self.backend == 'muselsl':
