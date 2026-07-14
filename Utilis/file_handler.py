from pathlib import Path
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


def save_uploaded_file(uploaded_file):
    safe_name = secure_filename(uploaded_file.name)
    if not safe_name:
        raise ValueError("Invalid filename.")
    filepath = UPLOAD_FOLDER / safe_name
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return filepath