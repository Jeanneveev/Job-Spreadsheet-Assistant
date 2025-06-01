import os
import re
from flask import current_app

def get_preexisting_filenames() -> list[str]:
    """Gets the root filename of all pre-existing question group files
    from the upload folder, and database and returns it as a singular list
    """
    print("reached get_preexisting")
    #get from saves folder
    files_filenames:list[str]=[]
    save_folder=current_app.config["UPLOAD_FOLDER"]
    print(f"save folder is {save_folder}")
    files=os.listdir(save_folder)
    print(f"files are {files}")
    for file in files:
        # print(f"file is {file}")
        if re.match(r"^qg_.*\.json$", file):
            # print("matched")
            file_name=file.removeprefix("qg_").removesuffix(".json")
            files_filenames.append(file_name)
    #     else:
    #         print("didn't match")
    # print(f"files_filenames is {files_filenames}")
    #TODO: Get from database
    db_filenames:list[str]=[]
    #make a combined list with no duplicates
    all_filenames:list[str]=list(set(files_filenames + db_filenames))
    # print(f"all filenames are: {all_filenames}")
    return all_filenames