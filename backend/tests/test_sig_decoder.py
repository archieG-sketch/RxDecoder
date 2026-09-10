import pytest
from app.utils.sig_decoder import decode_sig_string

def test_sig_decoder_basic():
    sig = "1 tab PO BID PC x 7d"
    decoded = decode_sig_string(sig)
    assert "by mouth" in decoded
    assert "two times a day" in decoded
    assert "after meals" in decoded

def test_sig_decoder_prn():
    sig = "1 cap PO Q6H PRN for pain"
    decoded = decode_sig_string(sig)
    assert "by mouth" in decoded
    assert "every 6 hours" in decoded
    assert "as needed" in decoded

def test_sig_decoder_empty():
    assert decode_sig_string("") == "Take as directed by your doctor."
