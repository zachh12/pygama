import pandas as pd
import matplotlib.pyplot as plt
#plt.style.use('../../pygama/clint.mpl')
import numpy as np
import json
import sys, os
from transforms import *


def main(run):

    #Load runDB File for transform reference
    with open('runDB.json') as f:
        runDB = json.load(f)
    #for item in runDB:
    #    print(item)

    #Separate signal processing & calculations
    raw_to_dsp = runDB['build_options']['conf1']['raw_to_dsp_options']

    #Pull a waveform for testing
    df = pd.read_hdf("../../../data/coherent/tier1/t1_run1796.h5", key='ORSIS3316WaveformDecoder')
    wf = df.iloc[25][8:]
    plt.plot(wf)

    plt.plot(blsub(wf))
    plt.show()




if __name__ == '__main__':
    main(sys.argv[1])