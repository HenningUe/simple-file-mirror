# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys
import time
import progressbar
from progressbar.widgets import Bar, Percentage
from simplefilemirror.handler import DataSyncHandler, DataSyncHandlerConfig
from simplefilemirror import DirectoryGetter


def main():
    try:
        _main_unhandled()
    except Exception as ex:
        print("Unhandled exception occurred")
        print(ex.message)
        input("Press Enter to continue...")


def _main_unhandled():
    src_dir = DirectoryGetter.get_src_dir()
    trg_dir = DirectoryGetter.get_trg_dir()
    if trg_dir is None:
        print("Aborted.")
        input("Press Enter to continue...")
        return

    progress_hdl = ProgressHandler()
    cfg = DataSyncHandlerConfig(progress_callback=progress_hdl.inform_about_progress,
                                data_tagging_meta_root_dir=DirectoryGetter.get_drive_root(),
                                meta_dir_name="_syncdata", hide_meta_dir=True,
                                directory_blocklist=['EOSMISC'])
    datasync_hdl = DataSyncHandler(src_dir, trg_dir, cfg)
    print(f"Synchronising fotos from '{str(src_dir)}' to '{str(trg_dir)}'")
    datasync_hdl.sync_files_full()
    print("Successfully synchronized")
    time.sleep(3.0)


class ProgressHandler(object):

    _wait_between_progress_update = 0.0

    def __init__(self):
        try:
            chr_f = unichr  # @UndefinedVariable
        except Exception:
            chr_f = chr
        widg_bar = Bar(marker=chr_f(int('0x25a0', 16)), fill=chr_f(int('0x25a1', 16)))
        widgets = (widg_bar, Percentage(),)
        self.bar = progressbar.ProgressBar(max_value=100, redirect_stdout=True, fd=sys.stdout,
                                           # line_breaks=False,
                                           widgets=widgets)

    def inform_about_progress(self, procent, data):
        self.bar.update(procent)
        if self._wait_between_progress_update > 0:
            time.sleep(self._wait_between_progress_update)


if __name__ == "__main__":
    main()
