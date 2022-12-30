# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import subprocess
import re
import unittest
import platform

import _setup
import datasync


class TestBase(object):

    @classmethod
    def init(cls):
        _setup.init()

    @classmethod
    def finished(cls):
        pltf = platform.system().lower()
        if pltf == "windows":
            cmd = "explorer"
        elif pltf == "linux":
            cmd = "xdg-open"
        elif pltf == "darwin":
            cmd = "open"
        else:
            raise ValueError("System '{}' not supported".format(pltf))
        subprocess.Popen([cmd, _setup.TEST_ROOT])

    @classmethod
    def get_files_list(cls, struct_in):
        recmp = re.compile(r"^.*\.\w+$", re.IGNORECASE)
        return [x for x in struct_in if recmp.match(x)]

    @classmethod
    def get_files_to_be_deleted(cls, struct_in):
        recmp = re.compile(r"^.*deleteme.*$", re.IGNORECASE)
        return [x for x in struct_in if recmp.match(x)]

    @classmethod
    def get_pure_folder_struct(cls, struct_in):
        recmp = re.compile(r"^(.*?)(\.\w\w\w)$", re.IGNORECASE)
        folders = [x for x in struct_in if not recmp.match(x)]
        files = [x for x in struct_in if recmp.match(x)]
        folders2 = [os.path.dirname(x) for x in files]
        folders.extend(folders2)
        return folders


class TestHandlingSyncBase(TestBase):
    _TEST_DIR_STRUCT = None

    def _test_files_copied_properly(self):
        from simplefilemirror import DirectoryGetter
        files_list = self.get_files_list(self._TEST_DIR_STRUCT)
        for f in files_list:
            path_xchange_src = os.path.join(DirectoryGetter.get_src_dir(), f)
            path_local_trg = os.path.join(DirectoryGetter.get_trg_dir(), f)
            # xchange
            msg = "Missing at xchange: {}".format(path_xchange_src)
            self.assertTrue(os.path.isfile(path_xchange_src), msg)
            # local
            msg = "Missing at local: {}".format(path_local_trg)
            self.assertTrue(os.path.isfile(path_local_trg), msg)


class TestHandlingDeleteBase(TestBase):
    _TEST_DIR_STRUCT = None

    def _test_deleted_files_are_not_copied_second_time(self):
        from simplefilemirror import DirectoryGetter
        files_list = self.get_files_to_be_deleted(self._TEST_DIR_STRUCT)
        for f in files_list:
            msg = "Exists at xchange, deleted at local: {}".format(f)
            path_xchange_src = os.path.join(DirectoryGetter.get_src_dir(), f)
            path_local_trg = os.path.join(DirectoryGetter.get_trg_dir(), f)
            # xchange
            self.assertTrue(os.path.isfile(path_xchange_src), msg)
            # local
            self.assertFalse(os.path.isfile(path_local_trg), msg)


class TestHandlingSync1stRun(unittest.TestCase, TestHandlingSyncBase):

    @classmethod
    def setUpClass(cls):
        cls._TEST_DIR_STRUCT = _setup.TEST_DIR_STRUCT_IN_EXCHANGE_1
        _setup.create_folder_struct_1_in_test_exchange_dir()
        datasync.main()

    def test_files_copied_properly(self):
        self._test_files_copied_properly()


class TestHandlingDelete1stRun(unittest.TestCase, TestHandlingDeleteBase):

    @classmethod
    def setUpClass(cls):
        cls._TEST_DIR_STRUCT = _setup.TEST_DIR_STRUCT_IN_EXCHANGE_1
        _setup.delete_items_in_test_local_dir()
        datasync.main()

    def test_deleted_files_are_not_copied_second_time(self):
        self._test_deleted_files_are_not_copied_second_time()


class TestHandlingSync2ndRun(unittest.TestCase, TestHandlingSyncBase):

    @classmethod
    def setUpClass(cls):
        cls._TEST_DIR_STRUCT = _setup.TEST_DIR_STRUCT_IN_EXCHANGE_2
        _setup.create_folder_struct_2_in_test_exchange_dir()
        datasync.main()

    def test_files_copied_properly(self):
        self._test_files_copied_properly()


class TestHandlingDelete2ndRun(unittest.TestCase, TestHandlingDeleteBase):

    @classmethod
    def setUpClass(cls):
        cls._TEST_DIR_STRUCT = _setup.TEST_DIR_STRUCT_IN_EXCHANGE_2
        _setup.delete_items_in_test_local_dir()
        datasync.main()

    def test_deleted_files_are_not_copied_second_time(self):
        self._test_deleted_files_are_not_copied_second_time()


def run_test():
    print("++++ Start test suite ++++ ")
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestHandlingSync1stRun))
    testsuite.addTest(unittest.makeSuite(TestHandlingDelete1stRun))
    testsuite.addTest(unittest.makeSuite(TestHandlingSync2ndRun))
    testsuite.addTest(unittest.makeSuite(TestHandlingDelete2ndRun))
    TestBase.init()
    unittest.TextTestRunner().run(testsuite)
    TestBase.finished()
    print("++++ finished ++++ ")


if __name__ == '__main__':
    run_test()
