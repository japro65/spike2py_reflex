import numpy as np

import spike2py_reflex as s2pr


def calculate_outcomes(section):
    section = _calculate_outcomes(section)
    section = s2pr.calculate_outcomes_of_avg(section)
    section = s2pr.calculate_mean_outcomes(section)
    return section


def _calculate_outcomes(section):
    for muscle, reflexes in section.reflexes.items():
        if reflexes.type in [s2pr.SINGLE, s2pr.TRAIN]:
            section.reflexes[muscle] = _get_single_outcomes(reflexes)
        elif reflexes.type == s2pr.DOUBLE:
            section.reflexes[muscle] = _get_double_outcomes(reflexes)
    return section


def _get_single_outcomes(reflexes):

    x_axis = reflexes.x_axis_extract
    sd_all_idx, reflex_win_idx_all = get_required_idx(reflexes)

    for i in range(len(reflexes.reflexes)):
        waveform = reflexes.reflexes[i].waveform
        for reflex_type, reflex_idx_dict in reflex_win_idx_all.items():
            reflex_win_idx = reflex_idx_dict[reflexes.type]
            sd_idx = sd_all_idx[reflexes.type]
            outcomes, background_sd = get_outcomes_from_waveform(waveform, reflex_win_idx, sd_idx, x_axis)
            reflexes.reflexes[i].background_sd = background_sd
            if reflexes.reflexes[i].outcomes is None:
                reflexes.reflexes[i].outcomes = {reflex_type: outcomes}
            else:
                reflexes.reflexes[i].outcomes[reflex_type] = outcomes
    return reflexes


def get_required_idx(reflexes):
    sd_all_idx = reflexes.sd_window_idx
    reflex_win_idx_all = reflexes.reflex_windows_idx
    return sd_all_idx, reflex_win_idx_all


def _get_double_outcomes(reflexes):

    x_axis = reflexes.x_axis_extract
    sd_all_idx, reflex_win_idx_all = get_required_idx(reflexes)

    for i in range(len(reflexes.reflexes)):
        reflexes.reflexes[i].reflex1.outcomes = dict()
        reflexes.reflexes[i].reflex2.outcomes = dict()
        reflexes.reflexes[i].ratio = dict()

        waveform = reflexes.reflexes[i].waveform

        for reflex_type, reflex_idx_dict in reflex_win_idx_all.items():
            reflex_win_idx = reflex_idx_dict[reflexes.type]
            sd_idx = sd_all_idx[reflexes.type]

            # Reflex1
            reflex1_idx = reflex_win_idx[0]
            outcomes1, background_sd = get_outcomes_from_waveform(waveform, reflex1_idx, sd_idx, x_axis)
            reflexes.reflexes[i].reflex1.background_sd = background_sd
            reflexes.reflexes[i].reflex1.outcomes[reflex_type] = outcomes1

            # Reflex2
            if reflex_win_idx[1] is not None:
                reflex2_idx = reflex_win_idx[1]
                outcomes2, background_sd = get_outcomes_from_waveform(waveform, reflex2_idx, sd_idx, x_axis)
                reflexes.reflexes[i].reflex2.background_sd = background_sd
                reflexes.reflexes[i].reflex2.outcomes[reflex_type] = outcomes2
                if outcomes2.peak_to_peak is not None:
                    ratio = outcomes2.peak_to_peak / outcomes1.peak_to_peak
                else:
                    ratio = None
                reflexes.reflexes[i].ratio[reflex_type] = ratio
    return reflexes


def get_outcomes_from_waveform(waveform, reflex_idx, sd_win_idx, x_axis):
    onset = None
    amplitude = _get_amplitude(waveform, reflex_idx[0], reflex_idx[1])
    area = _get_area(waveform, reflex_idx[0], reflex_idx[1])
    onset_idx, background_sd = _get_onset(waveform, reflex_idx, sd_win_idx)
    if onset_idx is not None:
        onset = x_axis[onset_idx]
    outcomes = s2pr.Outcomes(amplitude, area, onset)
    return outcomes, background_sd


def _get_amplitude(reflex_waveform, idx1, idx2):
    min_idx = np.argmin(reflex_waveform[idx1:idx2])
    max_idx = np.argmax(reflex_waveform[idx1:idx2])
    min_val = reflex_waveform[min_idx]
    max_val = reflex_waveform[max_idx]
    if max_val > 0:
        amplitude = max_val - min_val
    else:
        amplitude = max_val + min_val
    return amplitude


def _get_area(waveform, idx1, idx2):
    reflex_waveform = np.abs(waveform[idx1:idx2] - np.mean(waveform[idx1:idx2]))
    return np.trapz(reflex_waveform)


def _get_onset(waveform, reflex_idx, sd_win_idx):
    abs_reflex = abs(waveform)
    background_sd = np.std(abs_reflex[sd_win_idx[0] : sd_win_idx[1]])
    threshold = background_sd * s2pr.SD_MULTIPLIER
    threshold_crossed = sum(abs_reflex[reflex_idx[0] : reflex_idx[1]] > threshold)
    if threshold_crossed:
        crossing_idx = _get_crossing_idx(abs_reflex, reflex_idx, threshold)
        return _get_onset_idx(abs_reflex, crossing_idx), background_sd
    else:
        return None, None


def _get_crossing_idx(abs_reflex, reflex_idx, threshold):
    for i in range(reflex_idx[0], reflex_idx[1]):
        if abs_reflex[i] > threshold:
            return i


def _get_onset_idx(abs_reflex, crossing_idx):
    for i in range(crossing_idx):
        if _inflexion_back_up(abs_reflex, crossing_idx):
            return crossing_idx - 1
        else:
            crossing_idx -= 1


def _inflexion_back_up(abs_reflex, crossing_idx):
    return abs_reflex[crossing_idx - 1] > abs_reflex[crossing_idx]
