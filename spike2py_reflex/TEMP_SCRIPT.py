from pathlib import Path
import spike2py
import spike2py_reflex as s2pr

study_path = Path("/home/martin/Dropbox/Martin/sketchbook/python/projects/spike2py_reflex/tests/data/study1/")
plot = False
info = s2pr.Info(study_path, plot)

for subject_ in info.subjects:
    info.clear_subject()
    info.init_subject(subject_)

    for trial_name, sections in info.trials_sections.trials_sections.items():
        info.trial = trial_name
        for section_name in sections:
            info.clear_section()
            info.init_section(section_name)

info.clear_section()
info.trial = 'biphasic_high_fq'
info.init_section('hreflex')


def _load_section_data(section_pkl_path: Path) -> spike2py.trial:
    return spike2py.trial.load(section_pkl_path)


data = _load_section_data(info.section_pkl)
triggers = s2pr.Triggers(info, data)
info.triggers = triggers

section = s2pr.extract_reflexes(info, data)
section = s2pr.calculate_outcomes(section)
