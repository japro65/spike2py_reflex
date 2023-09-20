from pathlib import Path

import spike2py as s2p
import spike2py_reflex as s2pr


def process(study_path: Path, plot=False):
    """Extract reflexes for all trials of all subject for a study.

    Parameters
    ----------
    study_path: Path to study folder. Folder is to be structured as indicated in spike2py_preprocess docs
    plot: Flag indicating whether to generate plots
    """
    info = s2pr.Info(study_path, plot)

    # Iterate over each subject
    for subject_ in info.subjects:
        info.clear_subject()
        info.init_subject(subject_)

        # Iterate over each trial for the subject
        for trial, sections in info.trials_sections.trials_sections.items():
            info.trial = trial

            # Iterate over each section in the trial
            for section in sections:
                info.clear_section()
                info.init_section(section)
                data = s2p.trial.load(info.section_pkl)
                info.triggers = s2pr.Triggers(info, data)
                section_reflexes = s2pr.extract_reflexes(info, data)

                # if plot:
                #     plots.extracted_reflexes(extracted_reflexes)
                # extracted_reflexes = reflex_outcomes.process(extracted_reflexes)
                # _save_extracted_reflexes(extracted_reflexes_with_outcomes)
