##############################################################################
#
# xpdan            by Billinge Group
#                   Simon J. L. Billinge sb2896@columbia.edu
#                   (c) 2016 trustees of Columbia University in the City of
#                        New York.
#                   All rights reserved
#
# File coded by:    Timothy Liu, Christopher J. Wright
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
import os
import sys
import shutil
import asyncio
import numpy as np

import pytest

from xpdacq.xpdacq_conf import (glbl_dict,
                                configure_device,
                                xpd_configuration)

from xpdacq.xpdacq import CustomizedRunEngine
from xpdacq.beamtimeSetup import _start_beamtime
from xpdacq.utils import import_sample_info, ExceltoYaml
from xpdsim import db, cs700, xpd_pe1c, shctl1

from pkg_resources import resource_filename as rs_fn


@pytest.fixture(scope='module')
def bt(home_dir):
    # start a beamtime
    PI_name = 'Billinge '
    saf_num = 300000
    wavelength = 0.1812
    experimenters = [('van der Banerjee', 'S0ham', 1),
                     ('Terban ', ' Max', 2)]
    pytest_dir = rs_fn('xpdacq', 'tests/')
    bt = _start_beamtime(PI_name, saf_num,
                         experimenters,
                         wavelength=wavelength)
    xlf = '300000_sample.xlsx'
    src = os.path.join(pytest_dir, xlf)
    shutil.copyfile(src, os.path.join(glbl_dict['import_dir'], xlf))
    import_sample_info(saf_num, bt)
    # set simulation objects
    pe1c = xpd_pe1c # alias
    configure_device(db=db, shutter=shctl1,
                     area_det=pe1c, temp_controller=cs700)
    yield bt


@pytest.fixture(scope='function')
def fresh_xrun(bt):
    # create xrun
    xrun = CustomizedRunEngine(None)
    xrun.md['beamline_id'] = glbl_dict['beamline_id']
    xrun.md['group'] = glbl_dict['group']
    xrun.md['facility'] = glbl_dict['facility']
    xrun.ignore_callback_exceptions = False
    xrun.beamtime = bt
    # link mds
    xrun.subscribe(xpd_configuration['db'].insert, 'all')
    yield xrun


@pytest.fixture(scope='module')
def home_dir():
    stem = glbl_dict['home']
    config_dir = glbl_dict['xpdconfig']
    archive_dir = glbl_dict['archive_dir']
    os.makedirs(stem, exist_ok=True)
    yield glbl_dict
    for el in [stem, config_dir, archive_dir]:
        if os.path.isdir(el):
            print("flush {}".format(el))
            shutil.rmtree(el)
