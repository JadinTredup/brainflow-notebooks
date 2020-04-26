import os
import numpy as np
import pandas as pd

from mne import create_info, concatenate_raws, pick_types, Epochs
from mne.io import RawArray
from mne.io.edf import read_raw_edf
from mne.datasets import eegbci
from mne.event import find_events
from mne.channels import make_standard_montage

from brainflow.board_shim import BoardShim, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

import utils

class brainflowDataset:
    def __init__(self, paradigm, subject, board_type, layout=None):
        # Initialize class variables
        self.paradigm = paradigm
        self.board_type = board_type
        self.eeg_info = self._get_source_info(layout)
        self.subject = subject

    def _get_source_info(self, layout=None):
        """ Gets board-specific information from the Brainflow library

        Returns:
            eeg_channels
            sfreq
            channel_names
        """
        if self.board_type == 'synthetic':
            board_id = BoardIds.SYNTHETIC_BOARD.value
            eeg_channels, sfreq= self._get_board_info(board_id)
            channel_names = utils.SYNTHETIC_CHANNELS

        elif self.board_type == 'ganglion':
            board_id = BoardIds.GANGLION_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)

        elif self.board_type == 'cyton':
            board_id = BoardIds.CYTON_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)
            channel_names = utils.OPENBCI_STANDARD_8

        elif self.board_type == 'cyton_daisy':
            board_id = BoardIds.CYTON_DAISY_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)
            channel_names = utils.OPENBCI_STANDARD_16

        elif self.board_type == 'ganglion_wifi':
            board_id = BoardIds.GANGLION_WIFI_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)

        elif self.board_type == 'cyton_wifi':
            board_id = BoardIds.CYTON_WIFI_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)
            channel_names = utils.OPENBCI_STANDARD_8

        elif self.board_type == 'cyton_daisy_wifi':
            board_id = BoardIds.CYTON_DAISY_WIFI_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)
            channel_names = utils.OPENBCI_STANDARD_16

        elif self.board_type == 'brainbit':
            board_id = BoardIds.BRAINBIT_BOARD.value
            eeg_channels, sfreq = self._get_board_info(board_id)
            channel_names = utils.BRAINBIT_CHANNELS

        elif self.board_type == 'unicorn':
            board_id = BoardIds.UNICORN_BOARD.value
            eeg_channels, sfreq, channel_names = self._get_board_info(board_id)
            channel_names = utils.UNICORN_CHANNELS


        if layout:
            channel_names = layout

        return [eeg_channels, sfreq, channel_names]

    def _get_board_info(self, id):
        channels = BoardShim.get_eeg_channels(id)
        sfreq = BoardShim.get_sampling_rate(id)
        return channels, sfreq

    def _load_session_data(self, subject_name, run):
        """Loads the session data and event files for a single session for a single subject. The first 5 seconds
        of every session is a baseline that was used to wait for the signal to settle, so the first 5 seconds
        of every trial is also removed.

        Parameters:
             subject_name
             run
             path

        Returns:
            data
            events
        """
        data_fn = subject_name + '_' + self.paradigm + '_' + str(run) + '.csv'
        event_fn = subject_name + '_' + self.paradigm + '_' + str(run) + '_EVENTS.csv'
        data_path = os.path.join('data', data_fn)
        event_path = os.path.join('data', event_fn)
        print(data_path)
        data = DataFilter.read_file(data_path)

        # remove beginning 5 seconds where signal settles
        idx = 5 * self.eeg_info[1]
        data = data[:, idx:]

        events = pd.read_csv(event_path)
        return data, events

    def _create_stim_array(self, data, events):
        data_time = data[-1]
        events = events.values
        events[:, 1] += 1
        stim_array = np.zeros((1, len(data_time)))
        for event in events:
            insert_idx = np.where(data_time == event[-1])
            stim_array[0][insert_idx] = event[1]

        return stim_array

    def _add_stim_to_raw(self, raw, stim_data, ch_name):
        info = create_info([ch_name], raw.info['sfreq'], ['stim'])
        stim_raw = RawArray(stim_data, info)
        raw.add_channels([stim_raw], force_update_info=True)
        return raw

    def _scale_eeg_data(self, data):
        data[self.eeg_info[0]] *= 1e-6
        return data

    def filter_data_pre_raw(self, data, fcenter, bandwidth, order, filter_type):
        """Filters the OpenBCI data using the BrainFlow functions before creating an MNE Raw object.

        Parameters:
            data
            fcenter
            bandwidth
            order
            filter_type

        Returns:
            data
        """
        for channel in self.eeg_info[0]:
            if filter_type == 'bandpass':
                DataFilter.perform_bandpass(data[channel], self.eeg_info[1], fcenter, bandwidth, order, FilterTypes.BESSEL.value,
                                            0)
            elif filter_type == 'notch':
                DataFilter.perform_bandstop(data[channel], self.eeg_info[1], fcenter, bandwidth, order,
                                            FilterTypes.BUTTERWORTH.value, 0)
            elif filter_type == 'highpass':
                DataFilter.perform_highpass(data[channel], self.eeg_info[1], fcenter, order, FilterTypes.BUTTERWORTH.value, 0)
        return data

    def denoise_data_pre_raw(self, data, denoise_method):
        for channel in self.eeg_info[0]:
            if denoise_method == 'mean':
                DataFilter.perform_rolling_filter(data[channel], 3, AggOperations.MEAN.value)
            elif denoise_method == 'median':
                DataFilter.perform_rolling_filter(data[channel], 3, AggOperations.MEDIAN.value)
            else:
                DataFilter.perform_wavelet_denoising(data[channel], denoise_method, 3)
        return data

    def preprocess_eeg(self, data, notch=True, bandpass=True, denoise=True, denoise_method='coif3'):
        """Preprocessing pipeline for EEG data

        Parameters:
            data
            notch
            bandpass
            denoise
            denoise_method

        Returns:
            data
        """
        # Notch filter to remove line-frequency
        if notch:
            print("Notch filter")
            data = self.filter_data_pre_raw(data, 60, 2, 4, 'notch')
        # Bandpass filter
        if bandpass:
            print("Bandpass filter")
            data = self.filter_data_pre_raw(data, 26, 50, 3, 'bandpass')
        # Denoising
        if denoise:
            print("Denoise")
            data = self.denoise_data_pre_raw(data, denoise_method)

        return data

    def bci_to_raw(self, data):
        eeg_data = data[self.eeg_info[0], :]
        ch_types = ['eeg'] * len(self.eeg_info[0])
        #montage = make_standard_montage('standard_1005')
        montage = make_standard_montage('standard_1020')
        info = create_info(ch_names=self.eeg_info[2], sfreq=self.eeg_info[1], ch_types=ch_types)
        raw = RawArray(eeg_data, info)
        raw.set_montage(montage)
        return raw

    def load_session_to_raw(self, subject_name, run, preprocess=False):
        # Load data
        data, events = self._load_session_data(subject_name, run)
        # Scale data
        data = self._scale_eeg_data(data)
        # Create stim array
        stims = self._create_stim_array(data, events)
        if preprocess:
            # Preprocess data
            data = self.preprocess_eeg(data)
        raw = self.bci_to_raw(data)
        raw = self._add_stim_to_raw(raw, stims, 'STI')
        return raw

    def load_subject_to_raw(self, subject_name, runs, preprocess=True):
        raws = []
        for run in runs:
            raws.append(self.load_session_to_raw(subject_name, run, preprocess))
        raw = concatenate_raws(raws)
        return raw
