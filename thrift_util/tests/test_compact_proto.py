from thrift_util.compact_proto import decode_struct


def test_sample():
    data = b"\x18\x02IN\x18\x02GB(\x05Daman\x18\x02en" \
           b"\x15\xba\x82\x91b\x15\xd4\x0b\x15\xec\xed\xbbE\x15\x84\xf9\xbc\x13\x18\x06405/86" \
           b"(\a405/857\x15\x02\x15\xd6\xee\x80\xb6\x0b\x15\x04\x00"
    s = decode_struct(data)
    assert s == {
        1: b'IN', 2: b'GB', 4: b'Daman', 5: b'en',
        6: 102899869, 7: 746, 8: 72842102, 9: 20422210, 10: b'405/86',
        12: b'405/857', 13: 1, 14: 1533025195, 15: 2
    }


# def test_map():
#     data = b'\x08\x00\x01\x00\x00\x00\x00\r\x00\x02\x08\x0c\x00\x00\x00\x01' \
#            b'b>\xda\x02\r\x00\x01\x0b\x0b\x00\x00\x00\t\x00\x00\x00\x0bbind_status' \
#            b'\x00\x00\x00\x0249\x00\x00\x00\x05data1\x00\x00\x00Z' \
#            b'http://esx.bigo.sg/eu_live/g1/M0A/07/22/ZJIBAFtdqbuIQDrbAAAMUcPUyoYAANRcAOhOuYAAAxp099.jpg' \
#            b'\x00\x00\x00\x05data2\x00\x00\x00t' \
#            b'{"gender":"0","bigUrl":' \
#            b'"http://esx.bigo.sg/eu_live/g1/M08/07/22/YpIBAFtdqbuIXNoQAAEHU1ZEDUkAANRdAOMSXgAAQdr838.jpg"}' \
#            b'\x00\x00\x00\x05data4\x00\x00\x000{"auth_type":0,"auth_info":"","st":"Sry ......"}' \
#            b'\x00\x00\x00\x05data5\x00\x00\x00Z' \
#            b'http://esx.bigo.sg/eu_live/g1/M00/07/25/YpIBAFtdqbuIQOuvAAA7hRlee7cAANRewDDQHYAADud220.jpg' \
#            b'\x00\x00\x00\tnick_name\x00\x00\x00\rRAJA ALI JAAN\x00\x00\x00\tuser_name\x00\x00\x00\t12345ravi' \
#            b'\x00\x00\x00\x07version\x00\x00\x00\x03243\x00\x00\x00\x05yyuid' \
#            b'\x00\x00\x00\t141297288\x00\x08\x00\x03\x00\x00\x00\x00\x00'
#     s = decode_struct(data)
#     assert s
