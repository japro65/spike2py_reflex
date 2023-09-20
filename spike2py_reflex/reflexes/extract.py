from spike2py_preprocess.trial_sections import find_nearest_time_index

import spike2py_reflex as s2pr


def extract_reflexes(info, data):
    """Extract reflexes for all muscles (emg) in section."""
    stim_int = s2pr.get_stim_intensity(info, data)
    extracted = dict()
    for emg_name in info.channels.emg:
        emg = getattr(data, emg_name)
        info.windows.fs = emg.info.sampling_frequency
        extracted[emg_name] = _extract_reflexes(emg_name, emg, stim_int, info)
    return s2pr.SectionReflexes(info, extracted)


def _extract_reflexes(emg_name, emg, stim_intensities, info):
    if info.triggers.type in [s2pr.SINGLE, s2pr.TRAIN]:
        muscle_reflexes = _extract_single_reflexes(
            emg_name, emg, stim_intensities, info
        )
    elif info.triggers.type == s2pr.DOUBLE:
        muscle_reflexes = _extract_double_reflexes(
            emg_name, emg, stim_intensities, info
        )
    return muscle_reflexes


def _extract_single_reflexes(emg_name, emg, stim_intensities, info):
    reflexes = list()
    trigger_windows = _get_trigger_extract_windows_singles(info)

    for (idx1_extract, idx2_extract), intensity in zip(
        trigger_windows, stim_intensities
    ):
        reflexes.append(
           s2pr.Single(
                waveform=emg.values[idx1_extract:idx2_extract],
                extract_indexes=(idx1_extract, idx2_extract),
                stim_intensity=intensity,
            )
        )

    if info.triggers.type == s2pr.SINGLE:
        x_axis = info.windows.x_axes.single
    elif info.triggers.type == s2pr.TRAIN:
        x_axis = info.windows.x_axes.train_single_pulse

    muscle_reflexes = s2pr.Singles(
        x_axis_extract=x_axis,
        reflexes=reflexes,
        type=info.triggers.type,
        sd_window_idx=info.windows.idx_sd,
        sd_window_ms=info.windows.ms_sd,
        reflex_windows_idx=info.windows.idx_reflexes[emg_name],
        reflex_windows_ms=info.windows.ms_reflexes[emg_name],
    )
    return muscle_reflexes


def _get_single_reflex_window_idx(x_axis, relative_reflex_window_idx):
    absolute_reflex_window_idx = dict()
    for reflex_name, reflex_idx in relative_reflex_window_idx.items():
        idx1 = find_nearest_time_index(x_axis, reflex_idx[0] * s2pr.CONVERT_MS_TO_S)
        idx2 = find_nearest_time_index(x_axis, reflex_idx[1] * s2pr.CONVERT_MS_TO_S)
        absolute_reflex_window_idx[reflex_name] = [idx1, idx2]
    return absolute_reflex_window_idx


def _extract_double_reflexes(emg_name, emg, stim_intensities, info):
    reflexes = list()
    trigger_windows = _get_trigger_extract_windows_doubles(info)

    for (
        (idx1_extract, idx2_extract),
        (idx1_reflex1, idx2_reflex1),
        (idx1_reflex2, idx2_reflex2),
    ), (intensity) in zip(trigger_windows, stim_intensities):
        reflex1 = s2pr.Single(waveform=emg.values[idx1_reflex1:idx2_reflex1])
        reflex2 = None
        if idx1_reflex2 is not None:
            reflex2 = s2pr.Single(waveform=emg.values[idx1_reflex2:idx2_reflex2])
        double = s2pr.Double(
            waveform=emg.values[idx1_extract:idx2_extract],
            reflex1=reflex1,
            reflex2=reflex2,
            stim_intensity=intensity,
            extract_indexes=(idx1_extract, idx2_extract),
        )
        reflexes.append(double)

    muscle_reflexes = s2pr.Doubles(
        x_axis_extract=info.windows.x_axes.double,
        x_axis_singles=info.windows.x_axes.double_single_pulse,
        reflexes=reflexes,
        type=info.triggers.type,
        sd_window_idx=info.windows.idx_sd,
        sd_window_ms=info.windows.ms_sd,
        reflex_windows_idx=info.windows.idx_reflexes[emg_name],
        reflex_windows_ms=info.windows.ms_reflexes[emg_name],
    )
    return muscle_reflexes


def _get_trigger_extract_windows_singles(info):
    trigger_windows = list()
    trigger_type = s2pr.SINGLE
    if info.triggers.type == s2pr.TRAIN:
        trigger_type = s2pr.TRAIN_SINGLE_PULSE
    extract_idx = getattr(info.windows.idx_extract, trigger_type)
    for trigger_idx in info.triggers.extract:
        trigger_windows.append(_get_window(trigger_idx, extract_idx))
    if trigger_windows[0][0] < 0:
        trigger_windows.pop(0)
    return trigger_windows


def _get_window(trigger_idx, window_idx):
    if trigger_idx is None:
        return [None, None]
    lower = trigger_idx + window_idx[0]
    upper = trigger_idx + window_idx[1]
    return [lower, upper]


def _get_trigger_extract_windows_doubles(info) -> list:
    """Get windows to extract double, and each reflex individually

    Returns
    -------

    List of lists. Each item in list represents one double. For each of these, there are three pairs of indexes.
    These are to extract 1) the entire double, 2) the first reflex, and 3) the second reflex.

    e.g. [[extract_start, extract_end], [reflex1_start, reflex1_end], [reflex2_start, reflex2_end]] , ...]
    """
    trigger_windows = list()
    extract_idx = getattr(info.windows.idx_extract, info.triggers.type)
    double_idx = getattr(info.windows.idx_extract, "double_single_pulse")
    for trigger_idx_extract, trigger_idx_double in zip(
        info.triggers.extract, info.triggers.double
    ):
        extract = _get_window(trigger_idx_extract, extract_idx)
        reflex1 = _get_window(trigger_idx_double[0], double_idx)
        reflex2 = _get_window(trigger_idx_double[1], double_idx)
        trigger_windows.append([extract, reflex1, reflex2])
    return trigger_windows
