import os
from glob import glob
from time import time, sleep
from random import choice

import numpy as np
from pandas import DataFrame
import pygame

from brainflow import DataFilter, BoardShim, BoardIds, BrainFlowInputParams

from utils import get_fns


STD_PORT = '/dev/ttyUSB0'


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


class triggeredRecording:

    def __init__(self, activity=None, markernames=None):
        self.activity = activity
        self.board_prepared = False
        self.board_id = None
        self.params = None
        self.board = None
        self.max_trials = 500
        self.markernames = markernames

    def initialize_eeg(self, board_type='synthetic', connection_method='usb', usb_port=None):
        self.board_id, self.params = get_board_info(board_type, connection_method, usb_port)
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.board_prepared = True

    def _setup_graphics(self, width, height):
        fill_color = (0, 0, 0)
        self.mywin = pygame.display.set_mode((width, height), 0, 32)
        self.mywin.fill(fill_color)

    def run_trial(self, duration, subject, run):
        if self.board_prepared == False:
            self.board.prepare_session()
            self.board_prepared = True

        record_duration = np.float32(duration)
        print("Beginning EEG Stream; Wait 5 seconds for signal to settle... \n")
        self.board.start_stream()
        sleep(5)

        # Get starting time-stamp by pulling the last sample from the board and using its time stamp
        last_sample = self.board.get_current_board_data(1)
        start = last_sample[-1][0]

        # setup graphics
        self._setup_graphics()

        triggered_events = []

        while (time() - start) < record_duration:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    ts = time()
                    key = event.key
                    if key == pygame.K_1:
                        marker = 1
                    elif key == pygame.K_2:
                        marker = 2
                    elif key == pygame.K_3:
                        marker = 3
                    elif key == pygame.K_4:
                        marker = 4
                    elif key == pygame.K_5:
                        marker = 5
                    elif key == pygame.K_6:
                        marker = 6
                    elif key == pygame.K_7:
                        marker = 7
                    elif key == pygame.K_8:
                        marker = 8
                    elif key == pygame.K_9:
                        marker = 9
                    elif key == pygame.K_0:
                        marker = 10
                    total_event = [marker, ts]
                    triggered_events.append(total_event)

        # cleanup the session
        self.board.stop_stream()
        #self.board_prepared = False
        event_data = pd.DataFrame(triggered_events)
        data = self.board.get_board_data()
        data_fn, event_fn = get_fns(subject, run, self.erp)
        DataFilter.write_file(data, data_fn, 'w')
        self.mywin.close()
        event_data.to_csv(event_fn)

if __name__=="__main__":
    test_exp = triggeredRecording(activity='gaming')
    test_exp.initialize_eeg(board_type='synthetic')

    subject_name = 'kb_test'
    duration = 10
    trial_num = 3
    test_exp.run_trial(duration=duration,
                       subject=subject_name,
                       run=trial_num)