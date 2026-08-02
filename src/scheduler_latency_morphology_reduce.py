"""Registered reduction for the 15-minute scheduler-latency morphology characterisation."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

from consts import TRANSFORM_DIFF, TRANSFORM_RLE
from transforms import can_reconstruct, compute_transform

PACKETS = 9_000; SLICE = 300; BLOCK = 3_000; PILOT_THRESHOLD = 479_359
TRANSFORMS = {"RLE": TRANSFORM_RLE, "DIFF": TRANSFORM_DIFF}


def percentile(values, numerator, denominator):
    ordered = sorted(values)
    index = (2 * (len(ordered) - 1) * numerator + denominator) // (2 * denominator)
    return ordered[index]


def frac(value): return {"numerator": value.numerator, "denominator": value.denominator}

def zigzag(value): return 2 * value if value >= 0 else -2 * value - 1

def uleb(values):
    output = bytearray()
    for value in values:
        while True:
            byte = value & 0x7f; value >>= 7
            output.append(byte | (0x80 if value else 0))
            if not value: break
    return bytes(output)


def sign_counts(values):
    return {"positive": sum(v > 0 for v in values), "zero": sum(v == 0 for v in values),
            "negative": sum(v < 0 for v in values)}


def winner_counts(values): return {name: values.count(name) for name in ("RLE", "DIFF", "TIE")}


def groups(raw, winners, fractions, reductions, size, label):
    result = []
    for index, start in enumerate(range(0, PACKETS, size)):
        stop = start + size; raw_scope = raw[start * 10:stop * 10]
        result.append({f"{label}_index": index, "latency_median_ns": percentile(raw_scope, 1, 2),
            "winner_counts": winner_counts(winners[start:stop]),
            "median_compression_fraction": {t: frac(percentile(v[start:stop], 1, 2)) for t, v in fractions.items()},
            "reduction_sign_counts": {t: sign_counts(v[start:stop]) for t, v in reductions.items()}})
    return result


def analyze_channel(raw, signed):
    if len(raw) != 90_000: raise ValueError("channel requires 90000 values")
    packets = []; winners = []; fractions = {t: [] for t in TRANSFORMS}; reductions = {t: [] for t in TRANSFORMS}
    for packet_index, start in enumerate(range(0, len(raw), 10)):
        values = raw[start:start + 10]
        encoded = uleb([zigzag(v) for v in values] if signed else values)
        outcomes = {}; sizes = {}
        for name, operation in TRANSFORMS.items():
            transformed = compute_transform(operation, encoded)
            if not can_reconstruct(operation, encoded, transformed): raise ValueError("reconstruction failure")
            reduction = len(encoded) - len(transformed); ratio = Fraction(reduction, len(encoded))
            reductions[name].append(reduction); fractions[name].append(ratio); sizes[name] = len(transformed)
            outcomes[name] = {"output_length": len(transformed), "reduction_bytes": reduction,
                              "compression_fraction": frac(ratio)}
        winner = "RLE" if sizes["RLE"] < sizes["DIFF"] else "DIFF" if sizes["DIFF"] < sizes["RLE"] else "TIE"
        winners.append(winner)
        packets.append({"packet_index": packet_index, "encoded_length": len(encoded),
                        "encoded_sha256": hashlib.sha256(encoded).hexdigest(), "winner": winner,
                        "outcomes": outcomes})
    slices = groups(raw, winners, fractions, reductions, SLICE, "slice")
    blocks = groups(raw, winners, fractions, reductions, BLOCK, "block")
    block_medians = {t: [Fraction(b["median_compression_fraction"][t]["numerator"],
                                 b["median_compression_fraction"][t]["denominator"]) for b in blocks]
                     for t in TRANSFORMS}
    majorities = []
    for block in blocks:
        counts = block["winner_counts"]
        majorities.append("RLE" if counts["RLE"] * 2 > BLOCK else
                          "DIFF" if counts["DIFF"] * 2 > BLOCK else "NONE")
    switching = "RLE" in majorities and "DIFF" in majorities
    drift = any(max(v) - min(v) > Fraction(1, 15) for v in block_medians.values())
    support_by_transform = {t: (sign_counts(reductions[t])["positive"] >= 900 and
        any(b["reduction_sign_counts"][t]["positive"] * 2 > BLOCK for b in blocks)) for t in TRANSFORMS}
    return {"packet_count": PACKETS, "winner_counts": winner_counts(winners),
            "reduction_sign_counts": {t: sign_counts(v) for t, v in reductions.items()},
            "switching": switching, "block_drift": drift,
            "block_median_compression_fractions": {t: [frac(v) for v in vals] for t, vals in block_medians.items()},
            "positive_compression_support": {"supported": any(support_by_transform.values()),
                                             "by_transform": support_by_transform},
            "slices": slices, "blocks": blocks, "packets": packets}


def load_raw(path):
    encoded = path.read_bytes(); artifact = json.loads(encoded)
    if artifact.get("status") != "RAW_ONLY" or artifact.get("sample_count") != 90_001 or artifact.get("cadence_ns") != 10_000_000:
        raise ValueError("raw dimensions mismatch")
    records = artifact.get("records", [])
    if len(records) != 90_001: raise ValueError("raw record count mismatch")
    for index, record in enumerate(records):
        if record[0] != index or record[1] != records[0][1] + index * 10_000_000 or record[2] < record[1]:
            raise ValueError("raw timing integrity failure")
    return encoded, artifact


def distributions(values):
    return {"median": percentile(values, 1, 2), "p90": percentile(values, 9, 10),
            "p95": percentile(values, 95, 100), "p99": percentile(values, 99, 100),
            "p999": percentile(values, 999, 1000), "max": max(values)}


def tail_diagnostics(values):
    flags = [v > PILOT_THRESHOLD for v in values]
    occupancy = [sum(flags[i:i + 10]) for i in range(0, len(flags), 10)]
    longest = current = 0
    for flag in flags:
        current = current + 1 if flag else 0; longest = max(longest, current)
    slices = [any(flags[i:i + 3000]) for i in range(0, len(flags), 3000)]
    return {"threshold_ns": PILOT_THRESHOLD, "sample_count_above": sum(flags),
            "sample_fraction": frac(Fraction(sum(flags), len(flags))),
            "packet_counts": {"zero": sum(x == 0 for x in occupancy), "one": sum(x == 1 for x in occupancy),
                              "at_least_two": sum(x >= 2 for x in occupancy)},
            "longest_sample_run": longest, "slices_with_any": sum(slices), "slice_count": len(slices)}


def gate(sham, compile_arm, sd, cd):
    median_shift = any(abs(percentile([
        Fraction(b["median_compression_fraction"][t]["numerator"], b["median_compression_fraction"][t]["denominator"])
        for b in compile_arm["blocks"]], 1, 2) - percentile([
        Fraction(b["median_compression_fraction"][t]["numerator"], b["median_compression_fraction"][t]["denominator"])
        for b in sham["blocks"]], 1, 2)) > Fraction(1, 15) for t in TRANSFORMS)
    rle_c = Fraction(compile_arm["winner_counts"]["RLE"], PACKETS)
    rle_s = Fraction(sham["winner_counts"]["RLE"], PACKETS)
    morphology = (compile_arm["switching"] != sham["switching"] or
                  compile_arm["block_drift"] != sham["block_drift"] or median_shift or
                  abs(rle_c - rle_s) > Fraction(1, 5))
    physical = cd["p99"] >= 2 * sd["p99"]
    classification = ("PHYSICALLY_AND_MORPHOLOGICALLY_RESPONSIVE" if physical and morphology else
        "PHYSICALLY_RESPONSIVE_MORPHOLOGY_FLAT" if physical else
        "MORPHOLOGY_SHIFT_WITHOUT_REGISTERED_PHYSICAL_SHIFT" if morphology else "NO_REGISTERED_RESPONSE")
    return {"physically_responsive": physical, "morphology_responsive": morphology,
            "median_direction_prediction_confirmed": cd["median"] < sd["median"],
            "components": {"switching_changed": compile_arm["switching"] != sham["switching"],
                           "block_drift_changed": compile_arm["block_drift"] != sham["block_drift"],
                           "block_median_shift": median_shift,
                           "rle_winner_fraction_shift": abs(rle_c - rle_s) > Fraction(1, 5)},
            "classification": classification}


def main():
    p = argparse.ArgumentParser(); p.add_argument("sham", type=Path); p.add_argument("compile", type=Path); p.add_argument("output", type=Path)
    a = p.parse_args(); sb, s = load_raw(a.sham); cb, c = load_raw(a.compile)
    if s["arm"] != "S" or c["arm"] != "C": raise ValueError("arm labels mismatch")
    arms = {}
    for name, artifact in (("S", s), ("C", c)):
        records = artifact["records"]
        late = [record[2] - record[1] for record in records][1:]
        dev = [(records[i][2] - records[i - 1][2]) - 10_000_000 for i in range(1, len(records))]
        arms[name] = {"distribution_ns": distributions(late), "tail_diagnostics": tail_diagnostics(late),
                      "deadline_lateness": analyze_channel(late, False),
                      "cadence_deviation_derivative": analyze_channel(dev, True)}
    primary = gate(arms["S"]["deadline_lateness"], arms["C"]["deadline_lateness"],
                   arms["S"]["distribution_ns"], arms["C"]["distribution_ns"])
    result = {"result_version": 1, "status": "VALID", "classification": primary["classification"],
              "primary_gate": primary, "arms": arms,
              "sources": {"S": {"path": str(a.sham), "sha256": hashlib.sha256(sb).hexdigest()},
                          "C": {"path": str(a.compile), "sha256": hashlib.sha256(cb).hexdigest()}},
              "prediction": "physical upper-tail response with flat direct packet morphology",
              "claim_boundary": "derivative descriptive; no feature-extractor redesign; no organism claims"}
    encoded = (json.dumps(result, separators=(",", ":"), sort_keys=True) + "\n").encode()
    fd = os.open(a.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream: stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({"output": str(a.output), "sha256": hashlib.sha256(encoded).hexdigest(),
        "classification": result["classification"], "primary_gate": primary,
        "distributions": {arm: data["distribution_ns"] for arm, data in arms.items()},
        "tail_diagnostics": {arm: data["tail_diagnostics"] for arm, data in arms.items()},
        "winners": {arm: data["deadline_lateness"]["winner_counts"] for arm, data in arms.items()},
        "positive_support": {arm: data["deadline_lateness"]["positive_compression_support"] for arm, data in arms.items()}}, indent=2, sort_keys=True))


if __name__ == "__main__": main()
