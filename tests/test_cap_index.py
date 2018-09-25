import pytest

from cap_sender.cap_index import read_form_type

@pytest.mark.parametrize('filename,expected', [
    ('123125125_123125!1231245212.pdf', 'APP'),
    ('21342341_134124!81724726.pdf', 'APP'),
    ('123125125_123125!123124_ST_23415212.pdf', 'ST'),
    ('123125125_123125!123124_TE_23415212.pdf', 'TE')
])
def test_read_form_type(filename, expected):
    assert read_form_type(filename) == expected
