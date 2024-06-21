import os
from sweater import app


def get_path_for_image(secured_filename, separate=False):
    folder = app.config["UPLOAD_IMAGE_DEST"]
    if separate:
        return folder, secured_filename
    return os.path.join(folder, secured_filename)
