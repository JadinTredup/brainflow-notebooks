import os
from time import time
from glob import glob
from random import choice
from optparse import OptionParser

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb.stimuli import FACE_HOUSE


def present(duration=120, eeg=None, save_fn=None):
    n_trials = 2010
    iti = 0.4
    soa = 0.3
    jitter = 0.2
    record_duration = np.float32(duration)
    markernames = [1, 2]

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        eeg.start(fn=save_fn)

    # Setup trial list
    image_type = np.random.binomial(1, 0.5, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor='testMonitor', units="deg")

    faces = list(map(load_image, glob(os.path.join(FACE_HOUSE, 'faces', '*_3.jpg'))))
    houses = list(map(load_image, glob(os.path.join(FACE_HOUSE, 'houses', '*.3.jpg'))))
    stim = [houses, faces]

    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()

    # Iterate through the events
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select and display image
        label = trials['image_type'].iloc[ii]
        image = choice(faces if label == 1 else houses)
        image.draw()

        # Push sample
        eeg.push_sample(marker=markernames[label], timestamp=time())
        mywin.flip()

        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # Cleanup
    eeg.stop()
    mywin.close()