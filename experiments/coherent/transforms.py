import numpy as np
import scipy.signal as signal

def blsub(wf):
    return wf - np.mean(wf[0:25])
    
def pz(wf, clk=100e6, decay):
    """
    pole-zero correct a waveform
    decay is in us, clk is in Hz
    """
    # get linear filter parameters, in units of [clock ticks]
    dt = decay * (1e10 / clk)
    rc = 1 / np.exp(1 / dt)
    num, den = [1, -1], [1, -rc]

    # reversing num and den does the inverse transform (ie, PZ corrects)
    return signal.lfilter(den, num, wf)

def trap(wf, clk=100e6, rise, flat, fall=None, decay=0):
    """
    trapezoid filter.
    inputs are in microsec (rise, flat, fall, decay)
    """

    # convert params to units of [num samples, i.e. clock ticks]
    nsamp = 1e10 / clk
    rt, ft, dt = int(rise * nsamp), int(flat * nsamp), decay * nsamp
    flt = rt if fall is None else int(fall * nsamp)

    # calculate trapezoids
    if rt == flt:
        """
        symmetric case, use recursive trap (fastest)
        """
        tr1, tr2, tr3 = np.zeros_like(wfs), np.zeros_like(wfs), np.zeros_like(
            wfs)
        tr1[:, rt:] = wfs[:, :-rt]
        tr2[:, (ft + rt):] = wfs[:, :-rt - ft]
        tr3[:, (rt + ft + flt):] = wfs[:, :-rt - ft - flt]
        scratch = (wfs - tr1) - (tr2 - tr3)
        atrap = np.cumsum(scratch, axis=1) / rt
    else:
        """
        asymmetric case, use the fastest non-recursive algo i could find.
        (I also tried scipy.ndimage.convolve1d, scipy.signal.[fft]convolve)
        TODO (someday): change this to be recursive (need to math it out)
        https://www.sciencedirect.com/science/article/pii/0168900294910111
        """
        kernel = np.zeros(rt + ft + flt)
        kernel[:rt] = 1 / rt
        kernel[rt + ft:] = -1 / flt
        atrap = np.zeros_like(wfs)  # faster than a list comprehension
        for i, wf in enumerate(wfs):
            atrap[i, :] = np.convolve(wf, kernel, 'same')
        npad = int((rt+ft+flt)/2)
        atrap = np.pad(atrap, ((0, 0), (npad, 0)), mode='constant')[:, :-npad]
        # atrap[:, -(npad):] = 0

    # pole-zero correct the trapezoids
    if dt != 0:
        rc = 1 / np.exp(1 / dt)
        num, den = [1, -1], [1, -rc]
        ptrap = signal.lfilter(den, num, atrap)    

    if dt != 0:
        return ptrap
    else:
        return atrap