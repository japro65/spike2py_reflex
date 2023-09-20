# TODO: Determine whether actually need to validate

def validate(muscle_reflexes, info):
    pass


def _singles(reflexes, reflex_section_info):
    data_length = [len(reflexes.x_axis)]
    for emg_name in reflex_section_info.channels.emg:
        try:
            for reflex in reflexes.reflexes[emg_name]:
                data_length.append(len(reflex.data))
        except KeyError:
            pass
    if len(set(data_length)) != 1:
        min_data_length = min(data_length)
        length = len(reflexes.x_axis)
        reflexes.x_axis = reflexes.x_axis[length - min_data_length :]
        for emg_name in reflex_section_info.channels.emg:
            try:
                for i in range(len(reflexes.reflexes[emg_name])):
                    length = len(reflexes.reflexes[emg_name][i].data)
                    reflexes.reflexes[emg_name][i].data = reflexes.reflexes[emg_name][i].data[
                        length - min_data_length :
                    ]
            except KeyError:
                pass
    return reflexes


def _doubles(reflexes, reflex_section_info):
    data_length = [len(reflexes.double_x_axis)]
    for emg_name in reflex_section_info.channels.emg:
        try:
            for reflex in reflexes.reflexes[emg_name]:
                data_length.append(len(reflex.reflex_1.data))
                if reflex.reflex_2:
                    data_length.append(len(reflex.reflex_2.data))
        except KeyError:
            pass
    if len(set(data_length)) != 1:
        min_data_length = min(data_length)
        length = len(reflexes.double_x_axis)
        reflexes.double_x_axis = reflexes.double_x_axis[length - min_data_length :]
        for emg_name in reflex_section_info.channels.emg:
            try:
                for i in range(len(reflexes.reflexes[emg_name])):
                    length1 = len(reflexes.reflexes[emg_name][i].reflex_1.data)
                    reflexes.reflexes[emg_name][i].reflex_1.data = reflexes.reflexes[emg_name][
                        i
                    ].reflex_1.data[length1 - min_data_length :]
                    if reflexes.reflexes[emg_name][i].reflex_2:
                        length2 = len(reflexes.reflexes[emg_name][i].reflex_2.data)
                        reflexes.reflexes[emg_name][i].reflex_2.data = reflexes.reflexes[emg_name][
                            i
                        ].reflex_2.data[length2 - min_data_length :]
            except KeyError:
                pass
    return reflexes
