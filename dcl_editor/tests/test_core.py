from __future__ import annotations

from dcl_editor.core.classifier import classify_block
from dcl_editor.core.extractor import extract_fields
from dcl_editor.core.normalizer import normalize_block
from dcl_editor.core.tokenizer import tokenize_blocks
from dcl_editor.io.indexer import DclIndexer
from dcl_editor.io.loader import load_blocks_from_stream


SAMPLE = (
    "Noise before<STX>CDA<CR><LF>"
    "FI<SP>TK01QN/AN<SP>TC-JTM<CR><LF>"
    "DT<SP>QXS<SP>ISTW<SP>170439<SP>J04A<CR><LF>"
    "-<SP><SP>DC1/CDA<SP>0439<SP>250417<SP>LTFM<SP>PDC<SP>108<CR><LF>"
    "THY1QN<SP>CLRD<SP>TO<SP>EDDN<SP>OFF<SP>36<SP>VIA<SP>VADEN1E<CR><LF>"
    "SQUAWK<SP>3270<SP>NEXT<SP>FREQ<SP>124.425<SP>ATIS<SP>S<CR><LF>"
    "QNH<SP>1024<CR><LF>"
    "TSAT<SP>0456<CR><LF>"
    "TOBT<SP>0455<CR><LF>"
    "DEP<SP>FREQ<SP>131.125<CR><LF>"
    "CLIMB<SP>VIA<SP>SID<SP>TO<SP>ALTITUDE<SP>8000<SP>FT<CR><LF>"
    "E069<CR><LF><ETX>tail"
)


def test_tokenize_blocks_extracts_raw_segments():
    blocks = tokenize_blocks(SAMPLE)
    assert len(blocks) == 1
    assert blocks[0].startswith("<STX>CDA")
    assert blocks[0].endswith("<ETX>")


def test_normalize_block_removes_control_words():
    raw = tokenize_blocks(SAMPLE)[0]
    clean = normalize_block(raw)
    assert "<" not in clean
    assert ">" not in clean
    assert "STX" not in clean
    assert "ETX" not in clean
    assert "THY1QN CLRD TO" in clean
    assert "\n" in clean


def test_classify_block_via_first_token():
    raw = "<STX>CLD<CR><LF>CALLSIGN<SP>DATA<CR><LF><ETX>"
    clean = normalize_block(raw)
    block_type = classify_block(clean.split("\n"))
    assert block_type == "CLD"


def test_classify_block_via_header_hint():
    raw = "<STX>FI<SP>TEST<CR><LF>-<SP>DC1/CDA<SP>FOO<CR><LF><ETX>"
    clean = normalize_block(raw)
    block_type = classify_block(clean.split("\n"))
    assert block_type == "CDA"


def test_normalize_block_ignores_leading_slash():
    raw = "<STX>/HEADER<CR><LF>/CONTENT<SP>VALUE<CR><LF><ETX>"
    clean = normalize_block(raw)
    assert clean.split("\n")[0] == "HEADER"
    assert clean.split("\n")[1] == "CONTENT VALUE"


def test_extract_fields_finds_callsign_and_summary():
    clean_lines = normalize_block(tokenize_blocks(SAMPLE)[0]).split("\n")
    fields = extract_fields(clean_lines)
    assert fields["callsign"] == "THY1QN"
    assert "THY1QN" in fields["summary"]
    assert fields["preview_text"].split("\n")[0].startswith("FI TK01QN")


def test_loader_creates_dcl_block():
    blocks = load_blocks_from_stream(SAMPLE)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.callsign == "THY1QN"
    assert block.type == "CDA"
    assert "CLRD TO EDDN" in block.full_block_text


def test_indexer_filters_by_callsign_and_type():
    blocks = load_blocks_from_stream(SAMPLE)
    indexer = DclIndexer()
    indexer.rebuild(blocks)
    filtered = indexer.filter("THY1", {"CDA"})
    assert len(filtered) == 1
    filtered_empty = indexer.filter("ABC", {"CDA"})
    assert filtered_empty == []
