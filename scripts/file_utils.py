import shutil
import os
import stat


def copy_and_update_file(source_path: str, dest_path: str, replacements: dict = {}):
    # update the file path with any replacements
    for key, value in replacements.items():
        dest_path = dest_path.replace(key, value)

    # make sure the dest folder exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # copy the file, with text replacements
    try:
        print(f"Copying: {source_path} --> {dest_path}")
        with open(source_path, "rt") as fin:
            file_data = fin.read()
            with open(dest_path, "wt") as fout:
                for key, value in replacements.items():
                    file_data = file_data.replace(key, value)
                fout.write(file_data)
    except UnicodeDecodeError:
        # if it's not a text file, then just do a plain copy, with no replacements
        shutil.copy2(source_path, dest_path)


def copy_and_update_dir(source_path: str, dest_path: str, replacements: dict = {}):
    for root, dirs, files in os.walk(source_path):
        path = root.split(os.sep)
        for file in files:
            s_path = os.path.join(*path, file)
            d_path = os.path.join(dest_path, *path[1:], file)
            copy_and_update_file(s_path, d_path, replacements)


def delete_folder(folder_path: str):
    """
    Deletes a folder, even if it contains files (os.rmdir() will fail if the folder is not empty)

    If the folder does not exist, it will do nothing.
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


def make_file_executable(file_path: str):
    """Add the user execute permission to the existing permissions of a file"""
    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
