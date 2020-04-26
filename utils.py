import os
import socket
import platform
from collections import OrderedDict
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt


SYNTHETIC_CHANNELS = ['T7', 'CP5', 'FC5', 'C3', 'C4', 'FC6', 'CP6', 'T8']


OPENBCI_STANDARD_8 = ['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2',
                      'F7' , 'F8' , 'F3', 'F4', 'T7', 'T8', 'P3', 'P4']


OPENBCI_STANDARD_16 = ['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2',
                       'F7' , 'F8' , 'F3', 'F4', 'T7', 'T8', 'P3', 'P4']


BRAINBIT_CHANNELS = ['T3', 'T4', 'O1', 'O2']


UNICORN_CHANNELS = ['Fz', 'C3', 'Cz', 'C4', 'Pz', 'PO7', 'Oz', 'PO8']


SDESIGN = ['O1',  'PO3',  'P7' , 'CP5', 'CP2', 'P8' ,  'PO4', 'O2',
           'P3', 'FC5', 'C3', 'CP1', 'P4', 'C4', 'FC6', 'CP6']



USB_LINUX = '/dev/ttyUSB0'

USB_WINDOWS = 'COM3'


def get_fns(subject, run, paradigm):

    data_fn = os.path.join('data', f'{subject}_{paradigm}_{run}.csv')
    event_fn = os.path.join('data', f'{subject}_{paradigm}_{run}_EVENTS.csv')

    return data_fn, event_fn


def get_openbci_usb(usb_port):
    """Gets the standard USB port for the OpenBCI USB dongle
    """
    if usb_port is None:
        if platform.system() == 'Linux':
            usb_port = USB_LINUX
        elif platform.system() == 'Windows':
            usb_port = USB_WINDOWS
        elif platform.system() == 'Darwin':
            print('Please provide name of usb port for Mac OS')
            return None

    return usb_port


def get_openbci_ip(address, port):
    if address == None:
        address = '192.168.4.1'

    if port == None:
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]

    return address, port


def plot_conditions(epochs, conditions=OrderedDict(), ci=97.5, n_boot=1000,
                    title='', palette=None, ylim=(-6, 6),
                    diff_waveform=(1, 2)):
    """Plot ERP conditions.
    Args:
        epochs (mne.epochs): EEG epochs
    Keyword Args:
        conditions (OrderedDict): dictionary that contains the names of the
            conditions to plot as keys, and the list of corresponding marker
            numbers as value. E.g.,
                conditions = {'Non-target': [0, 1],
                               'Target': [2, 3, 4]}
        ci (float): confidence interval in range [0, 100]
        n_boot (int): number of bootstrap samples
        title (str): title of the figure
        palette (list): color palette to use for conditions
        ylim (tuple): (ymin, ymax)
        diff_waveform (tuple or None): tuple of ints indicating which
            conditions to subtract for producing the difference waveform.
            If None, do not plot a difference waveform
    Returns:
        (matplotlib.figure.Figure): figure object
        (list of matplotlib.axes._subplots.AxesSubplot): list of axes
    """
    if isinstance(conditions, dict):
        conditions = OrderedDict(conditions)

    if palette is None:
        palette = sns.color_palette("hls", len(conditions) + 1)

    X = epochs.get_data() * 1e6
    times = epochs.times
    y = pd.Series(epochs.events[:, -1])

    fig, axes = plt.subplots(2, 2, figsize=[12, 6],
                             sharex=True, sharey=True)
    axes = [axes[1, 0], axes[0, 0], axes[0, 1], axes[1, 1]]

    for ch in range(4):
        for cond, color in zip(conditions.values(), palette):
            sns.tsplot(X[y.isin(cond), ch], time=times, color=color,
                       n_boot=n_boot, ci=ci, ax=axes[ch])

        if diff_waveform:
            diff = (np.nanmean(X[y == diff_waveform[1], ch], axis=0) -
                    np.nanmean(X[y == diff_waveform[0], ch], axis=0))
            axes[ch].plot(times, diff, color='k', lw=1)

        axes[ch].set_title(epochs.ch_names[ch])
        axes[ch].set_ylim(ylim)
        axes[ch].axvline(x=0, ymin=ylim[0], ymax=ylim[1], color='k',
                         lw=1, label='_nolegend_')

    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylabel('Amplitude (uV)')
    axes[-1].set_xlabel('Time (s)')
    axes[1].set_ylabel('Amplitude (uV)')

    if diff_waveform:
        legend = (['{} - {}'.format(diff_waveform[1], diff_waveform[0])] +
                  list(conditions.keys()))
    else:
        legend = conditions.keys()
    axes[-1].legend(legend)
    sns.despine()
    plt.tight_layout()

    if title:
        fig.suptitle(title, fontsize=20)

    return fig, axes