
import os
import sys
import pathlib
try:
    import ConfigParser as configparser
except ImportError:
    import configparser as configparser
import re
import platform
import textwrap
import codecs

from . import _glob, _winapi


class DirectoryGetter(object):

    @classmethod
    def get_drive_root(cls):
        my_drive = _get_my_drive()
        return my_drive + "\\"

    @classmethod
    def get_src_dir(cls):
        src_dir = os.path.join(cls.get_drive_root(), "dcim")
        return src_dir

    @classmethod
    def get_trg_dir(cls):
        check_ini_file_ok = FileSyncIni.check_ini_file()
        if check_ini_file_ok is False:
            return None

        trgt_dir = FileSyncIni.read_target_dir()
        drive_name = _get_my_drive_name()
        trgt_dir = os.path.join(trgt_dir, drive_name)
        parent_parent = pathlib.Path(trgt_dir).parent.parent
        if not parent_parent.is_dir():
            msg = ("Target path's parent's parent is missing {}"
                   .format(str(parent_parent)))
            print(msg)
            return None
        return trgt_dir


class FileSyncIni(object):

    @classmethod
    def check_ini_file(cls):
        file_p = cls.get_config_file_path()
        if not os.path.isfile(file_p):
            cls.create_template()
            msg = ("Ini-file missing. Created at: {}"
                   .format(file_p))
            print(msg)
            return False
        else:
            computer_name = platform.node().lower()
            if not cls.is_secion_in_ini_file(computer_name):
                msg = ("in Ini-file '{}' section '{}' for this PC is missing."
                       .format(file_p, computer_name))
                print(msg)
                return False
        return True

    @classmethod
    def is_secion_in_ini_file(cls, section_to_test=None):
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read(cls.get_config_file_path())
        if section_to_test is None:
            computer_name = platform.node().lower()
            section_to_test = computer_name
        section_names = [s for s in cfg.sections()
                         if s.lower() == section_to_test]
        return any(section_names)

    @classmethod
    def read_target_dir(cls):
        if not cls.is_secion_in_ini_file():
            return None
        cfg = configparser.ConfigParser()
        cfg.read(cls.get_config_file_path())
        computer_name = platform.node().lower()
        section_names = [s for s in cfg.sections() if s.lower() == computer_name]
        trgt_dir = cfg.get(section_names[0], 'target_directory')
        if "%" in trgt_dir:
            regpat = "^(.*?)(\%.*?\%)(.*)$"
            re_m = re.match(regpat, trgt_dir)
            if re_m is not None:
                env_name = re_m.group(2)
                env_p = os.environ[env_name]
                trgt_dir = "".join([re_m.group(1), env_p, re_m.group(3)])
        return trgt_dir

    @classmethod
    def create_template(cls):
        tmpl = """
        [{computer_name}]
        # fill in the target dir. The section name is the PC-name. You can use environment vars
        target_directory=C:\\path\\to\\your\\fotos
        """
        tmpl = textwrap.dedent(tmpl)
        tmpl = tmpl[1:].format(computer_name=platform.node().lower())
        with codecs.open(cls.get_config_file_path(), "w", encoding="UTF-8") as f:
            f.write(tmpl)

    @classmethod
    def get_config_file_path(cls):
        my_drive = _get_my_drive()
        return os.path.join(my_drive + "\\", 'fotosync.ini')


def _get_my_drive_name():
    if _glob.my_drive_name is None:
        my_drive = _get_my_drive()
        drive_name = _winapi.get_volume_name(my_drive)
        return drive_name
    else:
        return _glob.my_drive_name


def _get_my_drive():
    if _glob.my_drive is None:
        my_file = sys.argv[0]  # __file__
        my_drive = os.path.splitdrive(my_file)[0]
        return my_drive
    else:
        return _glob.my_drive
