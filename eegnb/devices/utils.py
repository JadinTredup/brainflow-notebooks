import numpy as np
import socket
import platform


BRAINFLOW_CHANNELS = {
    'cyton' : [
        'Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2'
    ],
    'cyton_daisy' : [
        'Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2',
        'F7' , 'F8' , 'F3', 'F4', 'T7', 'T8', 'P3', 'P4'
    ],
    'brainbit' : [
        'T3', 'T4', 'O1', 'O2'
    ],
    'unicorn' : [
        'Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8'
    ],
    'synthetic':[
        'T7', 'CP5', 'FC5', 'C3', 'C4', 'FC6', 'CP6', 'T8'
    ]
}

def get_openbci_ip(address, port):
    if address == None:
        address = '192.168.4.1'

    if port == None:
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]

    return address, port

def get_openbci_usb():
    if platform.system() == 'Linux':
        return '/dev/ttyUSB0'
    elif platform.system() == 'Windows':
        return 'COM3'
    elif platform.system() == 'Darwin':
        return input("Please enter USb port for Mac OS")

def create_stim_array(timestamps, markers):
    num_samples = len(timestamps)
    stim_array = np.zeros((num_samples, 1))
    for marker in markers:
        stim_idx = np.where(timestamps == marker[1])
        stim_array[stim_idx] = marker[0]

    return stim_array