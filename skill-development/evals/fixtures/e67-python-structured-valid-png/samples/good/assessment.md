# Assessment

## P0: the generator cannot reach the behavior the test appears to cover

The signature assumption only turns arbitrary bytes into header-prefixed
malformed input. Almost every surviving example fails at a random chunk length,
unknown type, or CRC, which explains why `parse_ihdr`, IDAT inflation, filters,
and pixels are never reached. Ten thousand rejection-path examples are useful
for a narrow totality claim, but they do not test PNG semantics.

Split this into two properties:

1. Keep an arbitrary-byte malformed-input property. It should accept the
   documented `PNGError`, but unexpected exceptions such as `IndexError`,
   `OverflowError`, or assertion failures must escape and fail so Hypothesis can
   shrink and report them. Do not catch `Exception`.
2. Add a structured-valid composite strategy. Construct the PNG signature and
   an `IHDR` chunk followed by one or more `IDAT` chunks and `IEND`. For every
   chunk, derive the encoded length from its data and compute the CRC over the
   type plus data. Generate width/height in 1–256 and choose only bit-depth and
   color-type combinations allowed by the contract. Generate the matching
   number of raw scanline bytes (including filter bytes), zlib-compress them for
   IDAT, and keep interlace off. This makes every generated artifact coherent
   enough to reach filters and pixel decoding.

For the valid stream, assert semantics: decoded dimensions and pixels equal the
generated model, and encode/decode round-trips preserve that model. Validate a
sample of generated PNGs with an independent oracle such as Pillow or
`pngcheck`; otherwise a shared error in the builder and decoder could agree.
Track reachability per property—valid cases reaching `parse_ihdr`, `inflate_idat`
and every supported filter—not just Hypothesis's generated-example count.

After that, seed the arbitrary-byte test with valid files and mutations of the
valid corpus for the boundary between deep parsing and rejection. Increasing
`max_examples` alone cannot replace the structured generator.
More arbitrary examples do not solve structural reachability.
