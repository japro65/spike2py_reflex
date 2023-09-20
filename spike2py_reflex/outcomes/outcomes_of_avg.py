import numpy as np
import spike2py_reflex as s2pr
from spike2py_preprocess.trial_sections import find_nearest_time_index


def calculate_outcomes_of_avg(section):
    for muscle, reflexes in section.reflexes.items():
        stim_intensities = get_stim_intensities(reflexes)
        if reflexes.type in [s2pr.SINGLE, s2pr.TRAIN]:
            section.reflexes[muscle] = _single_calculate_avg(reflexes, stim_intensities)
        elif reflexes.type == s2pr.DOUBLE:
            info = section.info
            section.reflexes[muscle] = _double_calcualate_avg(reflexes, stim_intensities, info)
    return section


def _single_calculate_avg(reflexes, stim_intensities):
    reflexes.avg_waveform = dict()
    if _no_stim_intensities(stim_intensities):
        reflexes = _get_single_avg(reflexes, stim_intensities)
    else:
        for stim_intensity in stim_intensities:
            reflexes = _get_single_avg(reflexes, stim_intensity)
    return reflexes


def _no_stim_intensities(stim_intensities):
    return not stim_intensities


def get_stim_intensities(reflexes):
    stim_intensities = list()
    for reflex in reflexes.reflexes:
        if reflex.stim_intensity:
            stim_intensities.append(reflex.stim_intensity)
    if len(stim_intensities) == 0:
        return None
    return set(stim_intensities)


def _get_single_avg(reflexes, stim_intensity):

    # Get average waveform
    avg_reflex_waveform = list()
    for reflex in reflexes.reflexes:
        if (reflex.stim_intensity == stim_intensity) or (stim_intensity is None):
            avg_reflex_waveform.append(reflex.waveform)
    avg_reflex_waveform = np.array(avg_reflex_waveform).mean(axis=0)

    # Get values needed to compute outcomes
    x_axis = reflexes.x_axis_extract
    sd_all_idx, reflex_win_idx_all = s2pr.get_required_idx(reflexes)

    # Compute outcomes for reflex(es)
    all_outcomes = dict()
    for reflex_type, reflex_idx_dict in reflex_win_idx_all.items():
        reflex_win_idx = reflex_idx_dict[reflexes.type]
        sd_idx = sd_all_idx[reflexes.type]
        outcomes, background_sd = s2pr.compute_outcomes(avg_reflex_waveform, reflex_win_idx, sd_idx, x_axis)
        all_outcomes[reflex_type] = outcomes

    if stim_intensity is None:
        stim_intensity = 'no_intensity'
    reflexes.avg_waveform[stim_intensity] = s2pr.Single(waveform=avg_reflex_waveform,
                                                        outcomes=all_outcomes,
                                                        background_sd=background_sd)
    return reflexes


def _double_calcualate_avg(reflexes, stim_intensities, info):
    reflexes.avg_waveform = dict()
    reflexes.avg_reflex1 = dict()
    reflexes.avg_reflex2 = dict()

    if _no_stim_intensities(stim_intensities):
        reflexes = _get_double_avg(reflexes, stim_intensities, info)
    else:
        for stim_intensity in stim_intensities:
            reflexes = _get_double_avg(reflexes, stim_intensity, info)
    return reflexes


def _get_double_avg(reflexes, stim_intensity, info):
    # Get average waveform
    avg_reflex_waveform = list()
    for reflex in reflexes.reflexes:
        if (reflex.stim_intensity == stim_intensity) or (stim_intensity is None):
            avg_reflex_waveform.append(reflex.waveform)
    avg_reflex_waveform = np.array(avg_reflex_waveform).mean(axis=0)
    reflexes.avg_waveform[stim_intensity] = avg_reflex_waveform

    # Get values needed to compute outcomes
    x_axis = reflexes.x_axis_extract
    sd_all_idx, reflex_win_idx_all = s2pr.get_required_idx(reflexes)

    # Compute outcomes for reflex(es)
    all_outcomes_reflex1 = dict()
    all_outcomes_reflex2 = dict()

    for reflex_type, reflex_idx_dict in reflex_win_idx_all.items():
        reflex_win_idx = reflex_idx_dict[reflexes.type]
        sd_idx = sd_all_idx[reflexes.type]
        outcomes_reflex1, background_sd = s2pr.get_outcomes_from_waveform(avg_reflex_waveform, reflex_win_idx[0], sd_idx, x_axis)
        all_outcomes_reflex1[reflex_type] = outcomes_reflex1

        if reflex_win_idx[1] is not None:
            outcomes_reflex2, _ = s2pr.get_outcomes_from_waveform(avg_reflex_waveform, reflex_win_idx[1], sd_idx, x_axis)
            all_outcomes_reflex2[reflex_type] = outcomes_reflex2

    if stim_intensity is None:
        stim_intensity = 'no_intensity'

    idx_double_single_pulse = info.windows.idx_extract.double_single_pulse
    idx_time_zero = find_nearest_time_index(x_axis, 0)
    lower_idx1 = idx_time_zero + idx_double_single_pulse[0]
    upper_idx1 = idx_time_zero + idx_double_single_pulse[1]
    idx_time_isi = find_nearest_time_index(x_axis, info.windows.double_isi * s2pr.CONVERT_MS_TO_S)
    lower_idx2 = idx_time_isi + idx_double_single_pulse[0]
    upper_idx2 = idx_time_isi + idx_double_single_pulse[1]

    reflexes.avg_reflex1[stim_intensity] = s2pr.Single(waveform=avg_reflex_waveform[lower_idx1: upper_idx1],
                                                        outcomes=all_outcomes_reflex1,
                                                        background_sd=background_sd)

    reflexes.avg_reflex2[stim_intensity] = s2pr.Single(waveform=avg_reflex_waveform[lower_idx2: upper_idx2],
                                                       outcomes=all_outcomes_reflex2,
                                                       background_sd=background_sd)

    return reflexes
