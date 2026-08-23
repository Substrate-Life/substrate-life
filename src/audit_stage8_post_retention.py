"""Independent post-retention audit of the Stage 8 paired confirmatory artifacts
(docs/stage8-paired-post-retention-audit.md).  Added AFTER the f1e6880 freeze
as verification tooling only: read-only over results/, imported by no mechanic,
outside every frozen execution path (house precedent: audit_stage7b_signed_bracket.py).
Exact Fraction arithmetic throughout; recomputes endpoints and the section 5 rule
from the RAW artifact alone, then cross-checks the reduced artifact."""
import json, hashlib, sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

R = Path("/opt/data/avida-life")
raw_p = R / "results/stage8-alpha-evolution-paired/confirmatory-paired-20310529.json"
red_p = R / "results/stage8-alpha-evolution-paired/confirmatory-paired-20310529-reduced.json"
man_p = R / "results/stage8-alpha-evolution-paired/pre-execution-manifest.json"

raw = json.loads(raw_p.read_text())
red = json.loads(red_p.read_text())
man = json.loads(man_p.read_text())

checks = []
def ck(name, ok, detail=""):
    checks.append((name, bool(ok), detail))

# --- 1. hash binding ---------------------------------------------------------
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_size
for label, p in (("raw", raw_p), ("reduced", red_p)):
    h, b = sha(p)
    ck(f"{label}_artifact_hash_recorded", True, f"sha256={h[:16]}... bytes={b:,}")
sm = raw["source_manifest_sha256"]
mism = [f for f, h in sm.items()
        if f"src/{f}" in man["files"] and man["files"][f"src/{f}"]["sha256"] != h]
missing = [f for f in sm if f"src/{f}" not in man["files"]]
ck("raw_source_manifest_matches_freeze_pins", not mism and not missing,
   f"{len(sm)} FROZEN_SOURCES vs manifest pins; mismatches={mism} unpinned={missing}")

# --- 2..4 independent endpoint/rule recomputation ----------------------------
floor = Fraction(4, 255)
D, cls_ok, end_ok = {}, True, True
for pair in raw["pairs"]:
    rec = {}
    for arm in ("M", "R0"):
        a = pair["arms"][arm]
        hist = a["terminal_census"]["histogram_A"]
        n = sum(hist.values())
        mean = Fraction(sum(int(k) * v for k, v in hist.items()), 255 * n)
        if mean != Fraction(a["alpha_end"]) or \
           Fraction(a["terminal_census"]["alpha_mean"]) != mean:
            end_ok = False
        rec[arm] = mean
    d = rec["M"] - rec["R0"]
    D[pair["hazard_seed"]] = d
    want = "mover_up" if d >= floor else "mover_down" if d <= -floor else "non_mover"
    # Per-arm recorded classes are vs alpha_ref=3/5 at the 8/255 floor
    # (stage8_alpha_measure.direction_class), NOT vs the paired difference.
    from stage8_alpha_measure import direction_class as dc  # noqa: PLC0415
    for arm in ("M", "R0"):
        if pair["arms"][arm]["direction_class"] != dc(pair["arms"][arm]["alpha_end"]):
            cls_ok = False
ck("alpha_end_recomputed_bit_exact_from_terminal_histogram_all_48_arms", end_ok)
ck("recorded_direction_classes_match_registered_per_arm_semantics", cls_ok,
   "each arm's class == direction_class(alpha_end) vs alpha_ref 3/5 at floor 8/255")

k_eff = len(D)
up = sum(1 for d in D.values() if d >= floor)
dn = sum(1 for d in D.values() if d <= -floor)
nm = k_eff - up - dn
outcome = ("DEGENERATE_EVOLUTION" if k_eff < 16 else
           "ESTABLISHED_TOWARD_HIGH_ALPHA" if up >= 18 else
           "ESTABLISHED_TOWARD_LOW_ALPHA" if dn >= 18 else
           "NO_ESTABLISHED_DIRECTION")
ob = red["outcome_block"]
ck("independent_rule_replay_matches_retained_outcome",
   outcome == ob["outcome"] == "NO_ESTABLISHED_DIRECTION",
   f"k_eff={k_eff} up={up} down={dn} non={nm}; retained={ob['outcome']}")
ck("counts_block_matches_independent_counts",
   ob["counts"]["eligible_k_eff"] == k_eff and ob["counts"]["movers_up_pairs"] == up
   and ob["counts"]["movers_down_pairs"] == dn and ob["counts"]["non_mover_pairs"] == nm
   and ob["applied_exactly_once"] is True)

pdl = ob["descriptive"]["paired_differences"]
ok = True
rows = pdl.items() if isinstance(pdl, dict) else enumerate(pdl)
n_rows = 0
for key, item in rows:
    n_rows += 1
    if isinstance(item, dict):
        s = item.get("hazard_seed") or item.get("seed") or key
        dv = item.get("D") or item.get("difference") or item.get("paired_difference")
    else:
        s, dv = key, item
    if dv is None or D[int(s)] != Fraction(str(dv)):
        ok = False
ck("reduced_paired_difference_table_equals_independent", ok,
   f"{n_rows} rows compared bit-exactly")

desc = ob["descriptive"]
absD = sorted(abs(d) for d in D.values())
med_abs = (absD[11] + absD[12]) / 2 if len(absD) % 2 == 0 else absD[len(absD)//2]
ck("median_abs_D_matches_descriptive_block",
   Fraction(desc["median_abs_D_all_eligible"]) == med_abs,
   f"retained={desc['median_abs_D_all_eligible']} independent={med_abs} "
   f"(mid values {absD[11]},{absD[12]})")
ups = sorted(d for d in D.values() if d >= floor)
dns = sorted(d for d in D.values() if d <= -floor)
def med(v):
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2
mu, md = med(ups), med(dns)
ck("median_mover_blocks_match",
   Fraction(desc["median_D_among_movers_up"]) == mu
   and Fraction(desc["median_D_among_movers_down"]) == md,
   f"independent up_median={mu} down_median={md}; "
   f"retained up={desc['median_D_among_movers_up']} down={desc['median_D_among_movers_down']}")

# --- 5. leakage monitor + arm integrity -------------------------------------
bym = {p["hazard_seed"]: p for p in raw["pairs"]}
leak = []
for s, p in bym.items():
    ma = p["arms"]["M"]["terminal_census"].get("live_by_ancestry") or {}
    ra = p["arms"]["R0"]["terminal_census"].get("live_by_ancestry") or {}
    if ma and ra and max(ma, key=ma.get) != max(ra, key=ra.get):
        leak.append(s)
ck("terminal_plurality_leakage_monitor_clean_all_24_pairs", not leak,
   f"registered monitor (live_by_ancestry terminal plurality): divergent={leak}; "
   f"retained leakage_pairs={ob['counts']['leakage_pairs']}")

r0_ok, m_ok, g2_ok, gfz_ok, tick_ok = True, True, True, True, True
tel_note = ""
for p in raw["pairs"]:
    r0 = p["arms"]["R0"]; m = p["arms"]["M"]
    r0_tel = r0.get("mutation_telemetry") or {}
    if not (r0["kernel_draw_chain"] == [] and r0["classification"] == "COMPLETE"
            and r0_tel.get("decision_records") == 0 and r0_tel.get("draws_total") == 0
            and r0_tel.get("passes") is True and not r0_tel.get("problems")
            and r0["admitted_births_total"] > 0):
        r0_ok = False
    m_tel = m.get("mutation_telemetry") or {}
    if not (len(m["kernel_draw_chain"]) == m_tel.get("decision_records")
            == m_tel.get("admitted_births") + m_tel.get("memory_unavailable_failures", 0)
            and m_tel.get("admitted_births") == m["admitted_births_total"]
            and m_tel.get("draws_total", 0) >= len(m["kernel_draw_chain"])
            and m_tel.get("passes") is True and not m_tel.get("problems")
            and len(m["kernel_draw_chain"]) > 0):
        m_ok = False
    if not (m["tick_checkpoints"] == m["window_ticks"] + 2
            and m["closure_history_head"] == ["initial", "initial", "tick_complete:0"]
            and m["closure_history_tail"] == f"tick_complete:{m['window_ticks']-1}"
            and r0["tick_checkpoints"] == r0["window_ticks"] + 2):
        g2_ok = False
    if not (m["genome_freeze_audit"].get("passes") and r0["genome_freeze_audit"].get("passes")):
        gfz_ok = False
    if not (m["ticks_completed"] == m["window_ticks"] == 2400
            and not m["extinct"] and not r0["extinct"]):
        tick_ok = False
ck("R0_kernel_absence_pins_all_24", r0_ok)
ck("M_kernel_chain_vs_decision_records_reconciled_all_24", m_ok,
   "chain == decision_records == births + memory-unavailable (supply identity); "
   "draws_total >= chain (raw stream consumption incl. non-mutating decisions)")
ck("corrected_G2_closure_semantics_hold_at_W2400_all_48_arms", g2_ok,
   "tick_checkpoints == W+2 == 2402; head ['initial','initial','tick_complete:0']; tail 'tick_complete:2399'")
ck("genome_freeze_T128_D255_audits_pass_all_48_arms", gfz_ok)
ck("ticks_completed_W_zero_extinctions_all_48_arms", tick_ok)

ck("raw_protocol_and_table_echo", raw["protocol"] == red["protocol"]
   == "stage-8-alpha-evolution-repair-preregistration"
   and raw["seed_table"] == "confirmatory"
   and [p["hazard_seed"] for p in raw["pairs"]] == [20310529 + i for i in range(24)])

width = max(len(c[0]) for c in checks)
fails = 0
for name, okv, det in checks:
    print(f"{'PASS' if okv else 'FAIL'}  {name:<{width}}  {det}")
    fails += (not okv)
print(f"\n{len(checks) - fails}/{len(checks)} audit checks PASS; failures={fails}")
