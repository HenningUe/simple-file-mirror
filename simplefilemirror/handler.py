
import os
import codecs
import json
import fnmatch
import shutil
import datetime

from . import _winapi


class DataSyncHandlerConfig:

    def __init__(self,
                 file_exts_allowlist=None,
                 directory_blocklist=None,
                 store_meta_at_src=True, store_meta_at_trg=True,
                 meta_dir_name=None,
                 data_tagging_meta_root_dir=None,
                 hide_meta_dir=True,
                 number_meta_backup_files=10,
                 progress_callback=None,):
        if file_exts_allowlist is None:
            file_exts_allowlist = list()
        self.file_exts_allowlist = [fe.lower() for fe in file_exts_allowlist]
        if directory_blocklist is None:
            directory_blocklist = list()
        self.directory_blocklist = [dbl.lower() for dbl in directory_blocklist]
        self.store_meta_at_src = store_meta_at_src
        self.store_meta_at_trg = store_meta_at_trg
        self.meta_dir_name = meta_dir_name
        self.data_tagging_meta_root_dir = data_tagging_meta_root_dir
        self.hide_meta_dir = hide_meta_dir
        self.number_meta_backup_files = number_meta_backup_files
        self.progress_callback = progress_callback


class DataSyncHandler:

    def __init__(self, src_dir_root, trg_dir_root, data_sync_config=None):
        self.src_dir_root = src_dir_root
        self.trg_dir_root = trg_dir_root
        if data_sync_config is None:
            data_sync_config = DataSyncHandlerConfig()
        self.data_sync_config = data_sync_config
        tagging_src_root = self.src_dir_root
        if data_sync_config.data_tagging_meta_root_dir is not None:
            tagging_src_root = data_sync_config.data_tagging_meta_root_dir
        self._file_copier_tagger = FileCopierTagger(tagging_src_root, self.trg_dir_root,
                                                    data_sync_config.meta_dir_name,
                                                    data_sync_config.hide_meta_dir,
                                                    data_sync_config.number_meta_backup_files,
                                                    data_sync_config.store_meta_at_src,
                                                    data_sync_config.store_meta_at_trg)

    def sync_files_specific(self, last_changes):
        # example
        # last_changes =
        #     [{'action': u'Created',
        #       'file_dir_type': u'file',
        #       'full_filename': r'D:\Pictures\ft\new.jpg'}]
        copied_files = list()
        if len(last_changes) == 0:
            return copied_files
        already_copied_dataitem_list = self._file_copier_tagger.restore_dataitem_list()
        already_copied_dataitem_list = set(already_copied_dataitem_list)

        files_to_be_copied = list()
        for last_chg in last_changes:
            if last_chg['action'] not in ['Created'] \
               or last_chg['file_dir_type'] not in ['file'] \
               or (os.path.basename(os.path.dirname(last_chg['full_filename'])) ==
                   self._file_copier_tagger.META_DATA_DIR_NAME_DEFAULT):
                continue
            src_rel_path = os.path.relpath(last_chg['full_filename'], self.src_dir_root).lower()
            src_dir = os.path.basename(os.path.split(last_chg['full_filename'])[0])
            src_dir_top_lvl = src_rel_path.split(os.path.sep)[0]
            file_ext = os.path.splitext(src_rel_path)[1].lower()
            trg_file = os.path.normpath(os.path.join(self.trg_dir_root, src_rel_path))
            if src_dir.lower() in self.data_sync_config.directory_blocklist \
               or src_dir_top_lvl.lower() in self.data_sync_config.directory_blocklist \
               or (self.data_sync_config.file_exts_allowlist
                   and file_ext.lower() not in self.data_sync_config.file_exts_allowlist) \
               or src_rel_path in already_copied_dataitem_list:
                continue
            files_to_be_copied.append(
                dict(src=last_chg['full_filename'],  #pylint: disable=use-dict-literal
                trg=trg_file,
                src_rel=src_rel_path))
        return self._copy_files_to_be_copied(files_to_be_copied)

    def sync_files_full(self):
        already_copied_dataitem_list = self._file_copier_tagger.restore_dataitem_list()
        already_copied_dataitem_list = set(already_copied_dataitem_list)
        src_files_all = {os.path.join(x[0], y) for x in os.walk(self.src_dir_root) for y in x[2]
                         if (os.path.basename(x[0])
                             != self._file_copier_tagger.META_DATA_DIR_NAME_DEFAULT)}
        src_rel_files_all = {os.path.relpath(f, self.src_dir_root).lower() for f in src_files_all}
        trg_files = {os.path.join(x[0], y) for x in os.walk(self.trg_dir_root) for y in x[2]}
        trg_rel_files = {os.path.relpath(f, self.trg_dir_root).lower() for f in trg_files}
        files_to_be_copied = list()
        for src_rel_file in src_rel_files_all:
            if src_rel_file in already_copied_dataitem_list \
               or src_rel_file in trg_rel_files:
                continue
            source_file = os.path.join(self.src_dir_root, src_rel_file)
            file_ext = os.path.splitext(src_rel_file)[1].lower()
            src_dir = os.path.basename(os.path.split(source_file)[0])
            src_dir_top_lvl = src_rel_file.split(os.path.sep)[0]
            if src_dir.lower() in self.data_sync_config.directory_blocklist \
               or src_dir_top_lvl.lower() in self.data_sync_config.directory_blocklist \
               or (self.data_sync_config.file_exts_allowlist
                   and file_ext.lower() not in self.data_sync_config.file_exts_allowlist):
                continue
            target_file = os.path.join(self.trg_dir_root, src_rel_file)
            files_to_be_copied.append(dict(src=source_file,
                                           trg=target_file,
                                           src_rel=src_rel_file))
        return self._copy_files_to_be_copied(files_to_be_copied)

    def _copy_files_to_be_copied(self, files_to_be_copied):
        already_copied_dataitem_list = self._file_copier_tagger.restore_dataitem_list()
        already_copied_dataitem_list = set(already_copied_dataitem_list)
        copied_files = list()
        file_total_count = len(files_to_be_copied)
        for i_file, file_to_be_copied in enumerate(files_to_be_copied):
            src_file = file_to_be_copied['src']
            trg_file = file_to_be_copied['trg']
            src_rel_path = file_to_be_copied['src_rel']
            try:
                if not os.path.isdir(os.path.dirname(trg_file)):
                    os.makedirs(os.path.dirname(trg_file))
                shutil.copyfile(src_file, trg_file)
            except IOError:
                continue
            finally:
                if self.data_sync_config.progress_callback is not None:
                    progress = float(i_file + 1) / float(file_total_count) * 100.0
                    self.data_sync_config.progress_callback(progress, file_to_be_copied)
            already_copied_dataitem_list.add(src_rel_path)
            copied_files.append(src_rel_path)
        if any(copied_files):
            self._file_copier_tagger.store_dataitem_list(list(already_copied_dataitem_list))
        return copied_files


class FileCopierTagger(object):

    META_DATA_DIR_NAME_DEFAULT = "_data"
    _storage_file_name = "sync_file_list"

    def __init__(self, src_dir_path, trg_dir_path, meta_dir_name=None, hide_meta_dir=False,
                 number_back_ups=10,
                 store_meta_at_src=True, store_meta_at_trg=True):
        self._src_dir_path = src_dir_path
        self._trg_dir_path = trg_dir_path
        self._meta_dir_name = meta_dir_name
        self._hide_meta_dir = hide_meta_dir
        self._number_back_ups = number_back_ups
        self._store_meta_at_src = store_meta_at_src
        self._store_meta_at_trg = store_meta_at_trg
        self._last_datetime = None

    def store_dataitem_list(self, dataitem_list):
        if self._store_meta_at_src:
            self._store_dataitem_list(self._get_src_data_storage_dir(), dataitem_list)
        self._store_dataitem_list(self._get_trg_data_storage_dir(), dataitem_list)

    def restore_dataitem_list(self):
        if self._store_meta_at_src:
            storage_dir = self._get_src_data_storage_dir()
            dataitem_list = self._restore_dataitem_list(storage_dir)
            if not self._store_meta_at_trg \
               or (dataitem_list is not None and len(dataitem_list)):
                return dataitem_list
        if self._store_meta_at_trg:
            storage_dir = self._get_trg_data_storage_dir()
            dataitem_list = self._restore_dataitem_list(storage_dir)
            return dataitem_list

    def _restore_dataitem_list(self, storage_dir):
        existing_json_files = self._get_existing_json_backup_files(storage_dir)
        existing_json_files.sort(reverse=True)
        for existing_file in existing_json_files:
            source_json_file = os.path.join(storage_dir, existing_file)
            data = self._unserialize_from_json(source_json_file)
            if data is not None and len(data) and 'dataitem_list' in data:
                dataitem_list = data['dataitem_list']
                self._last_datetime = \
                    datetime.datetime.strptime(data['timestamp'], "%Y_%m_%d__%H_%M_%S")
                return dataitem_list
        return list()

    def _store_dataitem_list(self, storage_dir, dataitem_list):
        existing_json_files = self._get_existing_json_backup_files(storage_dir)
        existing_json_files.sort()
        if len(existing_json_files) >= self._number_back_ups:
            try:
                os.remove(os.path.join(storage_dir, existing_json_files[0]))
            except IOError:
                pass
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
        postfix = f"_{timestamp}.json"
        target_json_file = os.path.join(storage_dir, self._storage_file_name + postfix)
        data = dict(dataitem_list=dataitem_list, timestamp=timestamp)
        self._serialize_to_json(target_json_file, data)

    def _get_existing_json_backup_files(self, storage_dir):
        if not os.path.isdir(storage_dir):
            return list()
        fnmatch_pat = self._storage_file_name + "*"
        existing_json_files = [f.lower() for f in os.listdir(storage_dir)
                               if fnmatch.fnmatch(f, fnmatch_pat)]
        return existing_json_files

    def _get_src_data_storage_dir(self):
        path = os.path.join(self._src_dir_path, self._get_meta_dir_name())
        return path

    def _get_trg_data_storage_dir(self):
        path = os.path.join(self._trg_dir_path, self._get_meta_dir_name())
        return path

    def _get_meta_dir_name(self):
        if self._meta_dir_name is None:
            return self.META_DATA_DIR_NAME_DEFAULT
        else:
            return self._meta_dir_name

    @staticmethod
    def _serialize_to_json(json_target_file, dataitem_list):
        if not os.path.isdir(os.path.dirname(json_target_file)):
            storage_dir = os.path.dirname(json_target_file)
            os.makedirs(storage_dir)
            _winapi.set_file_attr_to_hidden(storage_dir)
        json_raw = json.dumps(dataitem_list)
        with codecs.open(json_target_file, 'w', encoding="utf-8") as f:
            f.write(json_raw)

    @staticmethod
    def _unserialize_from_json(json_source_file):
        if not os.path.isfile(json_source_file):
            return None
        with codecs.open(json_source_file, 'r', encoding="utf-8") as f:
            json_raw = f.read()
        try:
            data = json.loads(json_raw)
        except Exception:  # pylint: disable=broad-exception-caught
            return None
        return data
