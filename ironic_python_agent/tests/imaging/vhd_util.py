# Copyright 2013-2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib

import mock
from oslotest import base as test_base

from ironic_python_agent import errors
from ironic_python_agent.imaging import base
from ironic_python_agent.imaging import vhd_util
from ironic_python_agent.openstack.common import processutils


class TestVHDUtilImageManager(test_base.BaseTestCase):
    def setUp(self):
        super(TestVHDUtilImageManager, self).setUp()
        self.vhdutil_img_mgr = vhd_util.VHDUtilImageManager()

    @mock.patch('ironic_python_agent.utils.execute')
    def test__exec_untar(self, exec_mock):
        exec_mock.return_value = (None, None)
        exp_command = ['tar', '-C', 'tar dir', '-xSf', 'fake location']

        self.vhdutil_img_mgr._exec_untar('fake location', 'tar dir')

        exec_mock.assert_called_once_with(*exp_command,
                                          check_exit_code=[0])

    @mock.patch('ironic_python_agent.utils.execute')
    def test__exec_untar_fails(self, exec_mock):
        exec_mock.side_effect = processutils.ProcessExecutionError()
        exp_command = ['tar', '-C', 'tar dir', '-xSf', 'fake location']

        self.assertRaises(errors.ImageFormatError,
                          self.vhdutil_img_mgr._exec_untar,
                          'fake location',
                          'tar dir')

        exec_mock.assert_called_once_with(*exp_command,
                                          check_exit_code=[0])

    @mock.patch.object(vhd_util.VHDUtilImageManager, '_exec_untar')
    @mock.patch('os.mkdir')
    @mock.patch.object(base.BaseImageManager, '_safe_remove_path')
    @mock.patch.object(base.BaseImageManager, '_download_image')
    def test__untar_image(self, dl_mock, remove_mock, mkdir_mock, untar_mock):
        image_info = 'fake image info'

        @contextlib.contextmanager
        def _dl_side_effect(_data):
            yield 'fake location'

        dl_mock.side_effect = _dl_side_effect
        tardir = 'fake location.tardir'

        with self.vhdutil_img_mgr._untar_image(image_info) as loc:
            self.assertEqual(tardir, loc)
            dl_mock.assert_called_once_with(image_info)
            remove_mock.assert_called_once_with(loc)
            mkdir_mock.assert_called_once_with(loc)
            untar_mock.assert_called_once_with('fake location', loc)

        self.assertEqual([mock.call(tardir), mock.call(tardir)],
                         remove_mock.call_args_list)
