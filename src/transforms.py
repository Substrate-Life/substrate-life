"""Transform functions and reconstruction check (v3).

The substrate never inspects content for meaning. It applies a mechanical
transform and, separately, attempts a mechanical reconstruction of the
original bytes from the transformed output. Extraction is granted only when
reconstruction succeeds -- a structural property (information preserved),
not a designer whitelist of "approved" opcodes.
"""

import hashlib
from consts import TRANSFORM_RLE, TRANSFORM_DIFF, TRANSFORM_ENCODE_BASE, \
    TRANSFORM_FILTER_LOW, TRANSFORM_HASH_SUM


# --------------------------------------------------------------------------
# Forward transforms
# --------------------------------------------------------------------------

def compute_transform(op: int, data: bytes) -> bytes:
    """Apply a transform to data. Returns the transformed bytes.

    The substrate never inspects content -- it only returns the transformed
    output. The caller measures the size difference.
    """
    if op == TRANSFORM_RLE:
        return _run_length_encode(data)
    elif op == TRANSFORM_DIFF:
        return _diff_encode(data)
    elif op == TRANSFORM_ENCODE_BASE:
        return _base_encode(data)
    elif op == TRANSFORM_FILTER_LOW:
        return _filter_low(data)
    elif op == TRANSFORM_HASH_SUM:
        return _hash_sum(data)
    else:
        # Unknown transform: return data unchanged
        return data


def _run_length_encode(data: bytes) -> bytes:
    """RLE: repeated bytes become (count, byte) pairs."""
    if not data:
        return b""
    result = bytearray()
    i = 0
    while i < len(data):
        count = 1
        while i + count < len(data) and data[i + count] == data[i] and count < 255:
            count += 1
        result.append(count)
        result.append(data[i])
        i += count
    return bytes(result)


def _diff_encode(data: bytes) -> bytes:
    """Diff + RLE: store differences from previous byte, then RLE them."""
    if not data:
        return b""
    diffs = bytearray()
    prev = data[0]
    for b in data[1:]:
        diffs.append((b - prev) % 256)
        prev = b
    return bytes([data[0]]) + _run_length_encode(bytes(diffs))


def _base_encode(data: bytes) -> bytes:
    """Variable-length nibble packing. Common values (0-15) pack two per byte;
    others use an escape marker. Works well for biased distributions.
    """
    result = bytearray()
    i = 0
    while i < len(data):
        b = data[i]
        if b < 16 and i + 1 < len(data):
            n = data[i + 1]
            if n < 16:
                result.append((b << 4) | n)
                i += 2
                continue
        if b < 16:
            result.append(b << 4)
            i += 1
        else:
            result.append(0xF0 | (b >> 4))
            result.append(b & 0x0F)
            i += 1
    return bytes(result)


def _filter_low(data: bytes) -> bytes:
    """Lossy: keep only low 4 bits of each byte. Always halves size."""
    result = bytearray()
    for i in range(0, len(data) - 1, 2):
        lo = data[i] & 0x0F
        hi = data[i + 1] & 0x0F
        result.append((hi << 4) | lo)
    if len(data) % 2 == 1:
        result.append(data[-1] & 0x0F)
    return bytes(result)


def _hash_sum(data: bytes) -> bytes:
    """Lossy: SHA-256 digest. Always 32 bytes regardless of input. Irreversible."""
    return hashlib.sha256(data).digest()


# --------------------------------------------------------------------------
# Inverse transforms (used only by the reconstruction check)
# --------------------------------------------------------------------------

def _rle_decode(data: bytes) -> bytes | None:
    """Invert _run_length_encode. Returns None if the byte stream is malformed."""
    if not data:
        return b""
    if len(data) % 2 != 0:
        return None
    out = bytearray()
    for i in range(0, len(data), 2):
        count = data[i]
        value = data[i + 1]
        if count == 0:
            return None
        out.extend(bytes([value]) * count)
    return bytes(out)


def _diff_decode(data: bytes) -> bytes | None:
    """Invert _diff_encode."""
    if not data:
        return b""
    first = data[0]
    diffs = _rle_decode(data[1:])
    if diffs is None:
        return None
    out = bytearray([first])
    prev = first
    for d in diffs:
        cur = (prev + d) % 256
        out.append(cur)
        prev = cur
    return bytes(out)


def _base_decode(data: bytes) -> bytes | None:
    """Attempt to invert _base_encode.

    The encoding is ambiguous for some inputs (a packed pair whose high nibble
    is 15 collides with an escape marker). Where the decode does not reproduce
    the original, can_reconstruct() simply returns False and no energy is
    granted. No special-casing is applied -- the comparison decides.
    """
    out = bytearray()
    i = 0
    while i < len(data):
        b = data[i]
        if b >= 0xF1 and i + 1 < len(data) and data[i + 1] < 16:
            out.append(((b & 0x0F) << 4) | data[i + 1])
            i += 2
        else:
            hi = (b >> 4) & 0x0F
            lo = b & 0x0F
            out.append(hi)
            out.append(lo)
            i += 1
    return bytes(out)


_INVERSE = {
    TRANSFORM_RLE: _rle_decode,
    TRANSFORM_DIFF: _diff_decode,
    TRANSFORM_ENCODE_BASE: _base_decode,
}


def can_reconstruct(op: int, original: bytes, transformed: bytes) -> bool:
    """True iff the original bytes are recoverable from the transformed output.

    This is the extraction gate specified in project-report.md 1b. It is a
    mechanical check on information preservation: the substrate attempts a
    reconstruction and compares bytes. It never evaluates whether the data is
    meaningful, useful, or of a designer-preferred kind.

    Transforms with no inverse (HASH_SUM, FILTER_LOW) fail by construction --
    they reduce memory footprint but grant no energy.
    """
    inverse = _INVERSE.get(op)
    if inverse is None:
        return False
    try:
        recovered = inverse(transformed)
    except (IndexError, ValueError):
        return False
    if recovered is None:
        return False
    return recovered == original


if __name__ == "__main__":
    from datastream import DataStream

    stream = DataStream(seed=42)
    names = {
        TRANSFORM_RLE: "RLE", TRANSFORM_DIFF: "DIFF",
        TRANSFORM_ENCODE_BASE: "BASE", TRANSFORM_FILTER_LOW: "FILTER_LOW",
        TRANSFORM_HASH_SUM: "HASH_SUM",
    }
    for label, packet in (("rich", stream._rich_packet(0)),
                          ("lean", stream._lean_packet(0))):
        print(f"\n{label} packet ({len(packet.data)} bytes, "
              f"max_reducible={packet.max_reducible}):")
        for op, name in names.items():
            out = compute_transform(op, packet.data)
            ok = can_reconstruct(op, packet.data, out)
            share = (len(packet.data) - len(out)) / packet.max_reducible
            grant = packet.e_budget * share if (ok and len(out) < len(packet.data)) else 0.0
            print(f"  {name:<10} {len(packet.data):>3} -> {len(out):<4} "
                  f"lossless={str(ok):<5} extraction={grant:7.1f}")