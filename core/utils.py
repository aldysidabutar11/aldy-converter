import os

def get_unique_path(path):
    """If path exists, append (1), (2), etc. until a unique path is found."""
    if not os.path.exists(path):
        return path
    
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(f"{base} ({counter}){ext}"):
        counter += 1
    return f"{base} ({counter}){ext}"

def check_overwrite(path, ui_callback):
    """
    Checks if path exists. If it does, calls ui_callback.
    ui_callback should return:
    'overwrite' - proceed and delete existing
    'rename' - get a unique name
    'cancel' - abort operation
    """
    if not os.path.exists(path):
        return path, True

    res = ui_callback(path)
    if res == 'overwrite':
        return path, True
    elif res == 'rename':
        return get_unique_path(path), True
    else:
        return path, False
