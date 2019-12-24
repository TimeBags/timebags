'''
Global settings
'''
import os
import inspect
import ctypes
import shutil

def init():
    ''' Initializing env and global vars '''

    global path_conf_dir
    global path_tsa_dir
    global tsa_yaml
    global freetsa_pem

    # check/create conf dir
    home = os.path.expanduser("~")
    prefix = '.' if os.name != 'nt' else ''
    path_conf_dir = os.path.join(home, prefix + "timebags")
    if not os.path.exists(path_conf_dir):
        os.mkdir(path_conf_dir)
        if os.name == 'nt':
            if not ctypes.windll.kernel32.SetFileAttributesW(path_conf_dir, 0x02):
                raise ctypes.WinError()

    if not os.path.isdir(path_conf_dir):
        error = "unable to use configuration dir: " % path_conf_dir
        raise Exception(error)

    # check/create tsa files
    tsa_yaml = 'tsa.yaml'
    freetsa_pem = 'freetsa.pem'
    app_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    path_tsa_dir = os.path.join(path_conf_dir, 'tsa')
    if not os.path.exists(path_tsa_dir):
        os.makedirs(path_tsa_dir)
        shutil.copy(os.path.join(app_dir, tsa_yaml), path_tsa_dir)
        shutil.copy(os.path.join(app_dir, freetsa_pem), path_tsa_dir)
