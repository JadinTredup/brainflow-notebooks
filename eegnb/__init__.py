import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def generate_save_fn(board_name, experiment, subject_id):
    '''Generates a file name with the proper trial number for the current subject/experiment combo'''
    data_dir = os.path.join(DATA_DIR, experiment, subject_id)
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    # Check currently existing files to iterate to most recent trial number for the session/subject
    trial_num = 0
    file_name = f"{board_name}_TRIAL_{trial_num}.csv"
    save_fp = os.path.join(data_dir, file_name)
    while os.path.exists(save_fp):
        trial_num += 1
        file_name = f"{subject_id}_TRIAL_{trial_num}_{board_name}.csv"
        save_fp = os.path.join(data_dir, file_name)

    return save_fp