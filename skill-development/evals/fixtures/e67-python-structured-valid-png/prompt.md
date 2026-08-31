# Audit this parser test

Write an `assessment.md` for the following test and CI evidence. Recommend the
highest-value changes.

`tests/test_png_properties.py`:

```python
from hypothesis import assume, given, settings, strategies as st

from raster.png import PNGError, decode_png

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@settings(max_examples=10_000)
@given(st.binary(min_size=8, max_size=4096))
def test_png_decoder_never_crashes(data):
    assume(data.startswith(PNG_SIGNATURE))
    try:
        decode_png(data)
    except (PNGError, ValueError, IndexError, OverflowError):
        pass
```

`raster/png.py` accepts PNG files with this pipeline:

```text
signature -> chunk length/type/data/CRC -> IHDR validation -> IDAT inflate
          -> scanline filters -> pixels -> IEND
```

The current CI coverage report for the property is:

```text
check_signature       100%
read_chunk_header      94%
validate_chunk_crc      3%
parse_ihdr              0%
inflate_idat            0%
apply_scanline_filter   0%
decode_pixels           0%
```

The supported contract is non-interlaced images, dimensions 1–256, color
types grayscale and truecolor, and the PNG-defined bit depths valid for those
color types. `PNGError` is the documented response to malformed input.
