# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ctypes
import os


_DWORD = ctypes.c_ulong
MAX_PATH = ctypes.c_int(260)
MAX_PATH_NULL = int(MAX_PATH.value) + 1


def decode(s):
    if isinstance(s, str):
        return s
    return s.decode('mbcs')


def set_file_attr_to_hidden(file_path):
    cst_file_attr_hidden = 2
    ctypes.windll.kernel32.SetFileAttributesW(file_path,  # @UndefinedVariable
                                              cst_file_attr_hidden)


def get_volume_name(root_path_name):
    return get_volume_information(root_path_name)['volume_name']


def get_volume_information(root_path_name):
    global _DWORD
    vol_serial_number = _DWORD()
    max_comp_length = _DWORD()
    file_sys_flags = _DWORD()
    root_path_name = os.path.splitdrive(root_path_name)[0]

    if hasattr(ctypes.windll.kernel32, "GetVolumeInformationW"):
        root_path_name = decode(root_path_name)
        vol_name_buffer = ctypes.create_unicode_buffer(MAX_PATH_NULL)
        file_sys_name_buffer = ctypes.create_unicode_buffer(MAX_PATH_NULL)
        get_vol_info = ctypes.windll.kernel32.GetVolumeInformationW  # @UndefinedVariable
    else:
        vol_name_buffer = ctypes.create_string_buffer(MAX_PATH_NULL)
        file_sys_name_buffer = ctypes.create_string_buffer(MAX_PATH_NULL)
        get_vol_info = ctypes.windll.kernel32.GetVolumeInformationA  # @UndefinedVariable
    get_vol_info(root_path_name, vol_name_buffer, MAX_PATH_NULL,
                 ctypes.byref(vol_serial_number), ctypes.byref(max_comp_length),
                 ctypes.byref(file_sys_flags), file_sys_name_buffer, MAX_PATH_NULL)
    return dict(volume_name=vol_name_buffer.value,
                serial_number=vol_serial_number.value,
                file_system_name=file_sys_name_buffer.value,
                )


if __name__ == "__main__":
    print(get_volume_name(r"J:"))
