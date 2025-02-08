###
# Copyright CEA (Commissariat à l'énergie atomique et aux
# énergies alternatives) (2017-2025)
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
###

import ctypes
from enum import Enum

from .error import pico_check


def make_enum(name, fields):
    mappings = {}
    for i, f in enumerate(fields):
        mappings[i] = f
    return Enum(name, mappings)


def pico_load_device_lib(name):
    import platform

    if platform.system() == "Linux":
        from ctypes import cdll

        lib = cdll.LoadLibrary(f"lib{name}.so.2")
    elif platform.system() == "Darwin":
        raise NotImplementedError("MacOSX is not supported yet")
    else:
        from ctypes import windll
        from ctypes.util import find_library

        lib = windll.LoadLibrary(find_library(f"{name}.dll"))
    return lib


def pico_enumerate_serial(ps_enumerate_handle):
    from .error import PicoscopeApiError

    try:
        count = ctypes.c_int16(0)
        serial_len = ctypes.c_int16(4096)
        serial_buff = (ctypes.c_int8 * serial_len.value)()
        pico_check(
            ps_enumerate_handle(
                ctypes.byref(count), serial_buff, ctypes.byref(serial_len)
            )
        )

        serial_ids = bytes(serial_buff[: serial_len.value - 1]).decode()
        for serial_num in serial_ids.split(","):
            yield serial_num,
    except PicoscopeApiError:
        pass