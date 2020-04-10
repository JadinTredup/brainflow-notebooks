import os
from glob import glob
from time import time, sleep
from random import choice

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from brainflow import DataFilter, BoardShim, BoardIds, BrainFlowInputParams

from utils import get_fns


STD_PORT = 'dev/ttyUSB0'


def get_board_info(board_type='synthetic', connection='usb', usb_port=None):
    """ Gets the BarinFlow ID for the respective OpenBCI board in use

    Parameters:
        board_type (str): Type of base OpenBCI board (options: synthetic, cyton, daisy)
        connection (str): Connection method, either via USB dongle or the Wifi board

    Returns:
        board_id (int): Id value for the board in the BrainFlow API
        """
    params = BrainFlowInputParams()
    if usb_port is None:
        usb_port = STD_PORT

    if board_type == 'synthetic':
        board_id = BoardIds.SYNTHETIC_BOARD.value
    elif board_type == 'cyton':
        if connection == 'usb':
            board_id = BoardIds.CYTON_BOARD.value
            params.serial_port = usb_port
        elif connection == 'wifi':
            board_id = BoardIds.CYTON_WIFI_BOARD.value
    elif board_type == 'daisy':
        if connection == 'usb':
            board_id = BoardIds.CYTON_DAISY_BOARD.value
            params.serial_port = usb_port
        elif connection == 'wifi':
            board_id = BoardIds.CYTON_DAISY_WIFI_BOARD.value

    return board_id, params


def get_possible_ssvep_freqs(frame_rate, stim_type='single'):
    """ This function takes the frame rate of the monitor in use and returns the possible SSVEP
    stimulus frequencies based on the desired stimulus type.
    Credit: NeurotechX

    Parameters:
        frame_rate (int):
        stim_type (str):

    Returns:
        freqs
    """
    max_period_nb = int(frame_rate / 6)
    periods = np.arange(max_period_nb) + 1

    if stim_type == 'single':
        freqs = dict()
        for p1 in periods:
            for p2 in periods:
                f = frame_rate / (p1 + p2)
                try:
                    freqs[f].append((p1, p2))
                except:
                    freqs[f] = [(p1, p2)]
    elif stim_type == 'reversal':
        freqs = {frame_rate / p: [(p, p)] for p in periods[::-1]}

    return freqs

def init_flicker_stim(frame_rate, cycle, soa):
    """
    From NeurotechX EEG-Notebooks
    """
    if isinstance(cycle, tuple):
        stim_freq = frame_rate / sum(cycle)
        n_cycles = int(soa * stim_freq)
    else:
        stim_freq = frame_rate / cycle
        cycle = (cycle, cycle)
        n_cycles = int(soa * stim_freq) / 2

    return {'cycle': cycle,
            'freq' : stim_freq,
            'n_cycles' : n_cycles}


class eventRelatedPotential:

    def __init__(self, erp='n170'):
        self.erp = erp
        self.board_prepared = False
        self.board_id = None
        self.params = None
        self.board = None
        self.max_trials = 500
        self._setup_trial()

    def initialize_eeg(self, board_type='synthetic', connection_method='usb', usb_port=None):
        self.board_id, self.params = get_board_info(board_type, connection_method, usb_port)
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.board_prepared = True

    def _setup_trial(self):
        if self.erp == 'n170':
            self.image_type = np.random.binomial(1, 0.5, self.max_trials)
        if self.erp == 'p300':
            self.image_type = np.random.binomial(1, 0.5, self.max_trials)

        self.trials = DataFrame(dict(image_type=self.image_type,
                                     timestamp=np.zeros(self.max_trials)))

    def _setup_task(self):
        if self.erp == 'n170':
            self.markernames = ['houses', 'faces']
            self.markers = [1, 2]
        if self.erp == 'p300':
            self.markernames = ['nontargets', 'targets']
            self.markers = [1, 2]

    def _setup_graphics(self):
        self.mywin = visual.Window([1600, 900], monitor='testMonitor', units="deg")
        if self.erp == 'n170':
            faces = list(map(self._load_image, glob('stim/face_house/faces/*_3.jpg')))
            houses = list(map(self._load_image, glob('stim/face_house/houses/*.3.jpg')))
            self.stim = [houses, faces]
        if self.erp == 'p300':
            targets = list(map(self._load_image, glob('stim/cats_dogs/target-*.jpg')))
            nontargets = list(map(self._load_image, glob('stim/cats_dogs/nontarget-*.jpg')))
            self.stim = [nontargets, targets]

    def _load_image(self, fn):
        return visual.ImageStim(win=self.mywin, image=fn)

    def run_trial(self, duration, subject, run):
        if self.board_prepared == False:
            self.board.prepare_session()
            self.board_prepared = True
        # session information
        iti = 0.4
        soa = 0.3
        jitter = 0.2
        record_duration = np.float32(duration)
        print("Beginning EEG Stream; Wait 5 seconds for signal to settle... \n")
        self.board.start_stream()
        sleep(5)

        # Get starting time-stamp by pulling the last sample from the board and using its time stamp
        last_sample = self.board.get_current_board_data(1)
        start = last_sample[-1][0]

        # setup graphics
        self._setup_graphics()

        # iterate through events
        for ii, trial in self.trials.iterrows():
            # inter trial interval
            core.wait(iti + np.random.rand() * jitter)
            label = self.trials['image_type'].iloc[ii]
            image = choice(self.stim[label])
            image.draw()

            last_sample = self.board.get_current_board_data(1)
            timestamp = last_sample[-1][0]
            self.trials.loc[ii, 'timestamp'] = timestamp
            self.mywin.flip()

            # offset (Off-SET!)
            core.wait(soa)
            self.mywin.flip()
            if len(event.getKeys()) > 0 or (time() - start) > record_duration:
                break

            event.clearEvents()

        # cleanup the session
        self.board.stop_stream()
        #self.board_prepared = False
        data = self.board.get_board_data()
        data_fn, event_fn = get_fns(subject, run, self.erp)
        DataFilter.write_file(data, data_fn, 'w')
        self.mywin.close()
        self.trials.to_csv(event_fn)


class steadyStateEvokedPotentials:

    def __init__(self, paradigm='ssvep'):
        self.paradigm = paradigm
        self.board_id = None
        self.params = None
        self.board = None
        self.max_trials = 500
        self._setup_trials()

    def initialize_eeg(self, board_type='synthetic', connection_method='usb', usb_port=None):
        BoardShim.enable_dev_board_logger()
        self.board_id, self.params = get_board_info(board_type, connection_method, usb_port)
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()

    def _setup_trials(self):
        self.stim_freq = np.random.binomial(1, 0.5, self.max_trials)
        self.trials = DataFrame(dict(stim_freq=self.stim_freq,
                                     timestamp=np.zeros(self.max_trials)))

    def _setup_graphics(self):
        soa = 0.3
        self.mywin = visual.Window([1600, 900], monitor='testMonitor', units="deg", wintype='pygame')
        if self.paradigm == 'ssvep':
            grating = visual.GratingStim(win=self.mywin, mask='circle', size=80, sf=0.2)
            grating_neg = visual.GratingStim(win=self.mywin, mask='circle', size=80, sf=0.2, phase=0.5)
            frame_rate = np.round(self.mywin.getActualFrameRate())
            stim_patterns = [init_flicker_stim(frame_rate, 2, soa),
                                  init_flicker_stim(frame_rate, 3, soa)]

        return grating, grating_neg, stim_patterns

    def _load_image(self, fn):
        return visual.ImageStim(win=self.mywin, image=fn)

    def run_trial(self, duration, subject, run):
        # session information
        iti = 0.4
        jitter = 0.2
        record_duration = np.float32(duration)
        print("Beginning EEG Stream; Wait 5 seconds for signal to settle... \n")
        self.board.start_stream()
        sleep(5)

        # Get starting time-stamp by pulling the last sample from the board and using its time stamp
        last_sample = self.board.get_current_board_data(1)
        start = last_sample[-1][0]

        # setup graphics
        grating, grating_neg, stim_patterns = self._setup_graphics()

        # iterate through events
        for ii, trial in self.trials.iterrows():
            # inter trial interval
            core.wait(iti + np.random.rand() * jitter)
            label = self.trials['stim_freq'].iloc[ii]
            last_sample = self.board.get_current_board_data(1)
            timestamp = last_sample[-1][0]
            self.trials.loc[ii, 'timestamp'] = timestamp

            for _ in range(int(stim_patterns[label]['n_cycles'])):
                grating.setAutoDraw(True)
                for _ in range(int(stim_patterns[label]['cycle'][0])):
                    self.mywin.flip()
                grating.setAutoDraw(False)
                grating_neg.setAutoDraw(True)
                for _ in range(stim_patterns[label]['cycle'][1]):
                    self.mywin.flip()
                grating_neg.setAutoDraw(False)

            # Offset
            self.mywin.flip()
            if len(event.getKeys()) > 0 or (time() - start) > record_duration:
                break

            event.clearEvents()

        # cleanup the session
        self.board.stop_stream()
        data = self.board.get_board_data()
        data_fn, event_fn = get_fns(subject, run, self.paradigm)
        DataFilter.write_file(data, data_fn, 'w')
        self.mywin.close()
        self.trials.to_csv()
