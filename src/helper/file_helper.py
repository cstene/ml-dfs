import os

def rename_file(old, new):
    if(os.path.isfile(new)):
        os.remove(new)

    os.rename(old, new)