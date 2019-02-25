import os
from encode import encode_c480, encode_c720
from generate import genpat

def test_encode_c480():
    ans = True
    tmp_path = os.getcwd() + '/tmp'
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    fin = genpat(str(tmp_path))
    parsed = fin.split('.')
    fout = "".join(parsed[:-1]) + "_480p." + parsed[-1]

    succeed, output = encode_c480(fin, fout)

    if os.path.exists(fout):
        os.remove(fout)
    
    assert succeed == ans

def test_encode_c720():
    ans = True
    tmp_path = os.getcwd() + '/tmp'
    if not os.path.exists(tmp_path):
        os.mkdir(tmp_path)

    fin = genpat(str(tmp_path))
    parsed = fin.split('.')
    fout = "".join(parsed[:-1]) + "_720p." + parsed[-1]

    succeed, output = encode_c720(fin, fout)

    if os.path.exists(fout):
        os.remove(fout)
    
    assert succeed == ans