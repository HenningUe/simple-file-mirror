# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import shutil
import fnmatch
import inspect
import sys
import platform
import codecs
import textwrap
import tempfile

dir_ = os.path.dirname(inspect.getabsfile(lambda: None))
dir_ = os.path.dirname(dir_)
sys.path.append(dir_)

TEMP = tempfile.gettempdir()
TEST_ROOT = os.path.join(TEMP, "fotosync")
SRC_PATH = os.path.join(TEST_ROOT, r"sd_src")
DCIM_SRC_PATH = os.path.join(SRC_PATH, r"dcim")
TRG_PATH = os.path.join(TEST_ROOT, r"localfolder")

TEST_DIR_STRUCT_IN_EXCHANGE_1 = [
    r"mypic1.jpg",
    r"considerme\withsubfolder\valid0.jpg",
    r"ignoreme\withsubfolderNEWA\valid1.jpg",
    r"deleteme1.jpg",
    r"considerme1\empty\folder",
    r"considerme2\filled\valid2.jpg",

    r"x\mypic1.jpg",
    r"x\considerme\withsubfolder\valid0.jpg",
    r"x\ignoreme\withsubfolderNEWA\valid1.jpg",
    r"x\deleteme1.jpg",
    r"x\considerme1\empty\folder",
    r"x\considerme2\filled\valid2.jpg",

    r"xx\mypic1.jpg",
    r"xx\considerme\withsubfolder\valid0.jpg",
    r"xx\ignoreme\withsubfolderNEWA\valid1.jpg",
    r"xx\deleteme1.jpg",
    r"xx\considerme1\empty\folder",
    r"xx\considerme2\filled\valid2.jpg",

    r"cc\mypic1.jpg",
    r"cc\considerme\withsubfolder\valid0.jpg",
    r"cc\ignoreme\withsubfolderNEWA\valid1.jpg",
    r"cc\deleteme1.jpg",
    r"cc\considerme1\empty\folder",
    r"cc\considerme2\filled\valid2.jpg",

    r"cc\x\mypic1.jpg",
    r"cc\x\considerme\withsubfolder\valid0.jpg",
    r"cc\x\ignoreme\withsubfolderNEWA\valid1.jpg",
    r"cc\x\deleteme1.jpg",
    r"cc\x\considerme1\empty\folder",
    r"cc\x\considerme2\filled\valid2.jpg",

    r"cc\xx\mypic1.jpg",
    r"cc\xx\considerme\withsubfolder\valid0.jpg",
    r"cc\xx\ignoreme\withsubfolderNEWA\valid1.jpg",
    r"cc\xx\deleteme1.jpg",
    r"cc\xx\considerme1\empty\folder",
    r"cc\xx\considerme2\filled\valid2.jpg",
    ]

TEST_DIR_STRUCT_IN_EXCHANGE_2 = [
    r"considerme2\valid3.jpg",
    r"considerme2\deleteme.jpg",
    r"considerme3\deleteme\folder\pic3.jpg",
    r"considerme3\deleteme\folder\pic1.jpg",
    r"ignoreme\filled\folder\deleteme3.jpg",
    ]


def init():
    InitTasks.adapt_constants()
    InitTasks.clear_folders()


def create_folder_root_struct():
    global SRC_PATH
    global TRG_PATH
    for p in [SRC_PATH, TRG_PATH]:
        if os.path.isdir(p):
            _remove_dir(p)
        if not os.path.isdir(p):
            os.makedirs(p)


def create_folder_struct_1_in_test_exchange_dir():
    global TEST_DIR_STRUCT_IN_EXCHANGE_1, SRC_PATH
    FolderStructCreator.create_file_folder_struct(SRC_PATH,
                                                  TEST_DIR_STRUCT_IN_EXCHANGE_1)


def create_folder_struct_2_in_test_exchange_dir():
    global TEST_DIR_STRUCT_IN_EXCHANGE_2, SRC_PATH
    FolderStructCreator.create_file_folder_struct(SRC_PATH,
                                                  TEST_DIR_STRUCT_IN_EXCHANGE_2,
                                                  clear_before_creation=False)


def delete_items_in_test_local_dir():
    global TRG_PATH
    for root, dirs, files in os.walk(TRG_PATH, topdown=False):
        for name in files:
            if fnmatch.fnmatch(name, "*delete*"):
                os.remove(os.path.join(root, name))
        for name in dirs:
            if fnmatch.fnmatch(name, "*delete*"):
                shutil.rmtree(os.path.join(root, name), ignore_errors=True)


class InitTasks(object):

    @staticmethod
    def adapt_constants():
        global SRC_PATH
        import datasync
        datasync.ProgressHandler._wait_between_progress_update = 0.1
        from simplefilemirror import _glob
        _glob.my_drive = SRC_PATH
        # _glob.my_drive_name = "SD_CARD"

    @staticmethod
    def clear_folders():
        global SRC_PATH, TRG_PATH
        if os.path.isdir(SRC_PATH):
            _remove_dir(SRC_PATH)
        os.makedirs(SRC_PATH)
        if os.path.isdir(TRG_PATH):
            _remove_dir(TRG_PATH)
        os.makedirs(TRG_PATH)


class FolderStructCreator(object):

    @classmethod
    def create_file_folder_struct(cls, root_path, file_folder_struct, clear_before_creation=True):
        if clear_before_creation and os.path.isdir(root_path):
            _remove_dir(root_path)
        if not os.path.isdir(root_path):
            os.makedirs(root_path)
        cls.create_ini_file()
        dcim_dir = os.path.join(root_path, "dcim")
        for strc_item in file_folder_struct:
            fullpath = os.path.join(dcim_dir, strc_item)
            folder, file_ = cls._get_folder_and_file(fullpath)
            if not os.path.isdir(folder):
                os.makedirs(folder)
            if file_ and not os.path.isfile(fullpath):
                    cls._create_testfile(fullpath)

    @staticmethod
    def create_ini_file():
        global TRG_PATH
        from simplefilemirror import FileSyncIni
        tmpl = """
        [{computer_name}]
        # you can use environment vars
        target_directory={target_path}
        """
        tmpl = textwrap.dedent(tmpl)
        tmpl = tmpl[1:].format(computer_name=platform.node().lower(),
                               target_path=TRG_PATH)
        with codecs.open(FileSyncIni.get_config_file_path(), "w", encoding="UTF-8") as f:
            f.write(tmpl)

    @classmethod
    def _create_testfile(cls, fullfilepath):
        with open(fullfilepath, 'w') as f:
            longtxt = "\n".join(["x"*100] * 1000)
            f.write(longtxt)

    @classmethod
    def _get_folder_and_file(cls, fullfilepath):
        if cls._has_extension(fullfilepath):
            return os.path.split(fullfilepath)
        else:
            return fullfilepath, ""

    @classmethod
    def _has_extension(cls, fullfilepath):
        ext = os.path.splitext(fullfilepath)[1]
        return (not ext == "")


def _remove_dir(dir_path):
    os.system("rmdir /S /Q \"{}\"".format(dir_path))
    # shutil.rmtree(dir_path)
