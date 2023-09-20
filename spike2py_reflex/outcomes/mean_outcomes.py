import numpy as np

import spike2py_reflex as s2pr


def calculate_mean_outcomes(section):
    for muscle, reflexes in section.reflexes.items():

        stim_intensities = s2pr.get_stim_intensities(reflexes)

        if reflexes.type in [s2pr.SINGLE, s2pr.TRAIN]:
            reflexes.mean_outcomes = dict()
            section.reflexes[muscle] = _single_mean_outcomes(reflexes, stim_intensities)

        elif reflexes.type == s2pr.DOUBLE:
            reflexes.mean_outcomes_reflex1 = dict()
            reflexes.mean_outcomes_reflex2 = dict()
            reflexes.mean_ratio = dict()
            section.reflexes[muscle] = _double_mean_outcomes(reflexes, stim_intensities)

    return section


def _single_mean_outcomes(reflexes, stim_intensities):
    if _no_stim_intensities(stim_intensities):
        reflexes = _get_single_mean(reflexes, stim_intensities)
    else:
        for stim_intensity in stim_intensities:
            reflexes = _get_single_mean(reflexes, stim_intensity)
    return reflexes


def _no_stim_intensities(stim_intensities):
    return not stim_intensities


def _get_single_mean(reflexes, stim_intensity):

    _, reflex_win_idx_all = s2pr.get_required_idx(reflexes)

    # Extract outcomes for each reflex_type of interest (e.g. hreflex, mmax)
    for reflex_type, _ in reflex_win_idx_all.items():

        reflexes.mean_outcomes[reflex_type] = dict()

        peak_to_peak = list()
        peak_to_peak_none = 0
        peak_to_peak_yes = 0
        area = list()
        area_none = 0
        area_yes = 0
        onset = list()
        onset_none = 0
        onset_yes = 0

        for reflex in reflexes.reflexes:
            # For given intensity, make sure reflex elicited with that intensity
            # If no stim intensity available, include all reflexes
            if (reflex.stim_intensity == stim_intensity) or (stim_intensity is None):
                # peak-to-peak
                if reflex.outcomes[reflex_type].peak_to_peak is not None:
                    peak_to_peak.append(reflex.outcomes[reflex_type].peak_to_peak)
                    peak_to_peak_yes += 1
                else:
                    peak_to_peak_none += 1
                # area
                if reflex.outcomes[reflex_type].area is not None:
                    area.append(reflex.outcomes[reflex_type].area)
                    area_yes += 1
                else:
                    area_none += 1
                # onset
                if reflex.outcomes[reflex_type].onset is not None:
                    onset.append(reflex.outcomes[reflex_type].onset)
                    onset_yes += 1
                else:
                    onset_none += 1

        # Calculate mean outcome values

        # peak-to-peak
        if len(peak_to_peak) != 0:
            peak_to_peak = np.mean(peak_to_peak)
        else:
            peak_to_peak = None
        # area
        if len(area) != 0:
            area = np.mean(area)
        else:
            area = None
        # onset
        if len(onset) != 0:
            onset = np.mean(onset)
        else:
            onset = None

        outcomes = s2pr.Outcomes(peak_to_peak, area, onset)
        missing_outcomes = s2pr.Outcomes(peak_to_peak_none, area_none, onset_none)
        present_outcomes = s2pr.Outcomes(peak_to_peak_yes, area_yes, onset_yes)

        reflexes.mean_outcomes[reflex_type][str(stim_intensity)] = {"outcomes": outcomes,
                                                                    "missing_outcomes": missing_outcomes,
                                                                    "present_outcomes": present_outcomes}

    return reflexes


def _double_mean_outcomes(reflexes, stim_intensities):

    if _no_stim_intensities(stim_intensities):
        reflexes = _get_double_mean(reflexes, stim_intensities)
    else:
        for stim_intensity in stim_intensities:
            reflexes = _get_double_mean(reflexes, stim_intensity)
    return reflexes


def _get_double_mean(reflexes, stim_intensity):

    _, reflex_win_idx_all = s2pr.get_required_idx(reflexes)

    # Extract outcomes for each reflex_type of interest (e.g. hreflex, mmax)
    for reflex_type, _ in reflex_win_idx_all.items():

        reflexes.mean_ratio[reflex_type] = dict()
        reflexes.mean_outcomes_reflex1[reflex_type] = dict()
        reflexes.mean_outcomes_reflex2[reflex_type] = dict()

        peak_to_peak1 = list()
        peak_to_peak_none1 = 0
        peak_to_peak_yes1 = 0
        area1 = list()
        area_none1 = 0
        area_yes1 = 0
        onset1 = list()
        onset_none1 = 0
        onset_yes1 = 0

        peak_to_peak2 = list()
        peak_to_peak_none2 = 0
        peak_to_peak_yes2 = 0
        area2 = list()
        area_none2 = 0
        area_yes2 = 0
        onset2 = list()
        onset_none2 = 0
        onset_yes2 = 0

        ratio = list()
        ratio_none = 0
        ratio_yes = 0

        for reflex in reflexes.reflexes:
            # For given intensity, make sure reflex elicited with that intensity
            # If no stim intensity available, include all reflexes
            if (reflex.stim_intensity == stim_intensity) or (stim_intensity is None):
                # peak-to-peak
                if reflex.reflex1.outcomes[reflex_type].peak_to_peak is not None:
                    peak_to_peak1.append(reflex.reflex1.outcomes[reflex_type].peak_to_peak)
                    peak_to_peak_yes1 += 1
                else:
                    peak_to_peak_none1 += 1
                # area
                if reflex.reflex1.outcomes[reflex_type].area is not None:
                    area1.append(reflex.reflex1.outcomes[reflex_type].area)
                    area_yes1 += 1
                else:
                    area_none1 += 1
                # onset
                if reflex.reflex1.outcomes[reflex_type].onset is not None:
                    onset1.append(reflex.reflex1.outcomes[reflex_type].onset)
                    onset_yes1 += 1
                else:
                    onset_none1 += 1

                # peak-to-peak
                if reflex.reflex2.outcomes[reflex_type].peak_to_peak is not None:
                    peak_to_peak2.append(reflex.reflex2.outcomes[reflex_type].peak_to_peak)
                    peak_to_peak_yes2 += 1
                else:
                    peak_to_peak_none2 += 1
                # area
                if reflex.reflex2.outcomes[reflex_type].area is not None:
                    area2.append(reflex.reflex2.outcomes[reflex_type].area)
                    area_yes2 += 1
                else:
                    area_none2 += 1
                # onset
                if reflex.reflex2.outcomes[reflex_type].onset is not None:
                    onset2.append(reflex.reflex2.outcomes[reflex_type].onset)
                    onset_yes2 += 1
                else:
                    onset_none2 += 1

                if reflex.ratio[reflex_type] is not None:
                    ratio.append(reflex.ratio[reflex_type])
                    ratio_yes += 1
                else:
                    ratio_none += 1

        # Calculate mean outcome values

        # peak-to-peak
        if len(peak_to_peak1) != 0:
            peak_to_peak1 = np.mean(peak_to_peak1)
        else:
            peak_to_peak1 = None
        # area
        if len(area1) != 0:
            area1 = np.mean(area1)
        else:
            area1 = None
        # onset
        if len(onset1) != 0:
            onset1 = np.mean(onset1)
        else:
            onset1 = None

        # peak-to-peak
        if len(peak_to_peak2) != 0:
            peak_to_peak2 = np.mean(peak_to_peak2)
        else:
            peak_to_peak2 = None
        # area
        if len(area2) != 0:
            area1 = np.mean(area2)
        else:
            area2 = None
        # onset
        if len(onset2) != 0:
            onset2 = np.mean(onset2)
        else:
            onset2 = None

        if len(ratio) != 0:
            ratio = np.mean(ratio)
        else:
            ratio = None

        outcomes1 = s2pr.Outcomes(peak_to_peak1, area1, onset1)
        missing_outcomes1 = s2pr.Outcomes(peak_to_peak_none1, area_none1, onset_none1)
        present_outcomes1 = s2pr.Outcomes(peak_to_peak_yes1, area_yes1, onset_yes1)
        outcomes2 = s2pr.Outcomes(peak_to_peak2, area2, onset2)
        missing_outcomes2 = s2pr.Outcomes(peak_to_peak_none2, area_none2, onset_none2)
        present_outcomes2 = s2pr.Outcomes(peak_to_peak_yes2, area_yes2, onset_yes2)

        reflexes.mean_outcomes_reflex1[reflex_type][str(stim_intensity)] = {"outcomes": outcomes1,
                                                                            "missing_outcomes": missing_outcomes1,
                                                                            "present_outcomes": present_outcomes1}
        reflexes.mean_outcomes_reflex2[reflex_type][str(stim_intensity)] = {"outcomes": outcomes2,
                                                                            "missing_outcomes": missing_outcomes2,
                                                                            "present_outcomes": present_outcomes2}
        reflexes.mean_ratio[reflex_type][str(stim_intensity)] = {"ratio": ratio,
                                                                 "missing_ratio": ratio_none,
                                                                 "present_ratio": ratio_yes}

    return reflexes
