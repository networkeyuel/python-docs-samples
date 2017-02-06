# Copyright 2016, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

from transcribe import main


def test_main(resource, capsys):
    main(resource('audio.raw'))
    out, err = capsys.readouterr()

    assert re.search(r'how old is the Brooklyn Bridge', out, re.DOTALL | re.I)


def test_main_gcs(resource, capsys):
    main('gs://cloud-samples-tests/speech/brooklyn.flac')
    out, err = capsys.readouterr()

    assert re.search(r'how old is the Brooklyn Bridge', out, re.DOTALL | re.I)
