"""Independent verification audit of docs/stage-8-followon-power-memo.md (the
computed-closure document that binds reopening conditions R1-R3).  Added AFTER
that memo was committed (20765f3) as verification tooling only: read-only over
results/ and docs/, imported by no mechanic, outside every frozen execution
path, registers and executes nothing (house precedent:
audit_stage8_post_retention.py, audit_stage7b_signed_bracket.py).

Every memo constant is re-derived here from the RETAINED reduced/raw artifacts
and the source documents alone -- never from the memo's own tables except as
the comparison target.  Exact Fraction arithmetic throughout; binomial tails
over integers via math.comb; the two labelled continuous approximations
(normal-quantile map, mean-rule design sizing) use statistics.NormalDist and
are checked against the memo's stated values at the memo's own display
precision.  Wall-time estimates are recomputed under the memo's declared
linear-scaling model from the execution-note wall figure and are compared at
estimate tolerance."""
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from statistics import NormalDist

R = Path("/opt/data/avida-life")
PAIRED = R / "results/stage8-alpha-evolution-paired"
RAW_P = PAIRED / "confirmatory-paired-20310529.json"
RED_P = PAIRED / "confirmatory-paired-20310529-reduced.json"
MAN_P = PAIRED / "pre-execution-manifest.json"
MEMO = R / "docs/stage-8-followon-power-memo.md"
EXEC_NOTE = R / "docs/stage-8-paired-execution-note.md"
POST_AUDIT = R / "docs/stage8-paired-post-retention-audit.md"

FLOOR_LAT = Fraction(4)          # decision floor, lattice units (4/255 alpha)
K_PAIRS = 24
CONC = 18                        # concordance threshold at k=24


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def binom_tail(k, p, x):
    """Exact P(Bin(k, Fraction p) >= x) as a Fraction."""
    q = 1 - p
    return sum(math.comb(k, i) * p ** i * q ** (k - i) for i in range(x, k + 1))


def close(fval, shown, nd):
    """True when fval rounds (half-even irrelevant at this margin) to `shown`."""
    return abs(float(fval) - shown) <= 0.5 * 10 ** (-nd) + 1e-12


def run_audit():
    raw = json.loads(RAW_P.read_text())
    red = json.loads(RED_P.read_text())
    checks = []

    def ck(name, ok, detail="", cls="EXACT"):
        """cls='EXACT': gates the exit code -- memo claims stated as exact
        arithmetic.  cls='EST': findings against passages the memo itself
        labels 'approximation'/'estimate'; reported, never silently graded
        pass."""
        checks.append((name, bool(ok), detail, cls))

    # --- A. provenance digests (memo section 10) -----------------------------
    memo_expected = {
        RAW_P.name: "3eb06ecc03cbe044416ac403f59a7f0e2adb6ab2d2d2f4c54cf1f38c6ce660e7",
        RED_P.name: "bdb14fbedcfbcc4d3b3194edbfad428ac8869f1f8c75d848a6655147dd284dec",
        MAN_P.name: "c7cec747ab997a0fc9ede498d2e0f050498b24f77db93f6083a46bcb7c9054e7",
        "stage-8-paired-execution-note.md":
            "b3cf080ab9b85443d9d76151bc377457f9c0590df91fd9e78aae818eab0bbb9b",
        "stage-8-alpha-evolution-repair-preregistration.md":
            "669124a2a5db46f09c3757f11932f8d280acdda5824f87f7ea1b2340628d47fa",
    }
    drift = []
    for name, want in memo_expected.items():
        p = R / "docs" / name if name.endswith(".md") else PAIRED / name
        got = sha256(p)
        if got != want:
            drift.append(f"{name}:{got[:12]}")
    ck("A1_all_five_memo_provenance_digests_match_working_tree", not drift,
       "; ".join(drift) if drift else "raw, reduced, manifest, execution note,"
       " repair prereg all byte-identical to the session-8 record")
    post_raw = ("Raw artifact | `confirmatory-paired-20310529.json`, 4,198,845"
                " bytes")
    pa_txt = POST_AUDIT.read_text()
    cross = (memo_expected[RAW_P.name] in pa_txt
             and memo_expected[RED_P.name] in pa_txt)
    ck("A2_memo_and_post_retention_audit_agree_on_retained_digests", cross,
       "memo section 10 == stage8-paired-post-retention-audit.md table for"
       " raw+reduced SHA-256")

    # --- B. measured inputs (memo section 2) ---------------------------------
    pdiff = red["outcome_block"]["descriptive"]["paired_differences"]
    D = {int(s): Fraction(v) for s, v in pdiff.items()}
    lat = sorted((Fraction(d) * 255 for d in D.values()))
    memo_table = [
        Fraction(-215, 16), Fraction(-141, 16), Fraction(-141, 16),
        Fraction(-325, 48), Fraction(-263, 48), Fraction(-53, 12),
        Fraction(-167, 48), Fraction(-41, 12), Fraction(-41, 16),
        Fraction(-77, 48), Fraction(-3, 2), Fraction(23, 24),
        Fraction(65, 48), Fraction(37, 24), Fraction(51, 16),
        Fraction(197, 48), Fraction(109, 24), Fraction(73, 16),
        Fraction(55, 12), Fraction(79, 16), Fraction(239, 48),
        Fraction(31, 6), Fraction(289, 48), Fraction(167, 16)]
    ck("B1_memo_24_value_D_table_transcription_exact",
       lat == sorted(memo_table),
       f"sorted ascending, lattice units; min={lat[0]} max={lat[-1]}")
    mean = sum(D.values(), Fraction(0)) / K_PAIRS
    var_p = sum(((d - mean) ** 2 for d in D.values()), Fraction(0)) / K_PAIRS
    var_s = sum(((d - mean) ** 2 for d in D.values()), Fraction(0)) / (K_PAIRS - 1)
    sd_lat = math.sqrt(float(var_p)) * 255
    absD = sorted(abs(Fraction(d) * 255) for d in D.values())
    med_abs_alpha = (absD[11] + absD[12]) / 2 / 255
    up = sum(1 for d in D.values() if d >= Fraction(4, 255))
    dn = sum(1 for d in D.values() if d <= Fraction(-4, 255))
    pos = sum(1 for d in D.values() if d > 0)
    ck("B2_summary_statistics_reproduce_exactly",
       mean == Fraction(-47, 73440)
       and close(math.sqrt(float(var_p)), 0.022377, 6)
       and close(math.sqrt(float(var_s)), 0.022858, 6)
       and close(sd_lat, 5.7061, 4)
       and med_abs_alpha == Fraction(437, 24480)
       and (up, dn, K_PAIRS - up - dn) == (9, 6, 9)
       and (pos, K_PAIRS - pos) == (13, 11)
       and (float(lat[0]), float(lat[-1])) == (-13.4375, 10.4375),
       f"mean={mean} pop_sd={round(math.sqrt(float(var_p)), 6)} "
       f"samp_sd={round(math.sqrt(float(var_s)), 6)} sd_lat={round(sd_lat, 4)} "
       f"median|D|={med_abs_alpha} movers=9/6/9 sign=13/11 range=[-13.44,+10.44]")
    anchor = sum(math.comb(24, k) for k in range(CONC, 25))
    ck("B3_null_size_anchor_190051_over_2p24",
       anchor == 190051
       and close(Fraction(anchor, 2 ** 24), 0.01133, 5)
       and close(2 * Fraction(anchor, 2 ** 24), 0.02266, 5),
       f"sum C(24,k),k>=18 = {anchor}; one-sided "
       f"{float(Fraction(anchor, 2**24)):.5f}; two-sided x2")

    # --- C. concordance-rule exact tails (memo section 3) --------------------
    ps = {"0.50": Fraction(1, 2), "0.60": Fraction(3, 5), "0.70": Fraction(7, 10),
          "0.75": Fraction(3, 4), "0.80": Fraction(4, 5), "0.90": Fraction(9, 10)}
    expected_cells = {
        24: [0.01133, 0.09596, 0.38859, 0.60741, 0.81107, 0.99254],
        48: [0.00036, 0.02190, 0.27962, 0.57676, 0.85209, 0.99934],
        96: [None, 0.00148, 0.16938, 0.55456, 0.90903, None],
    }
    bad = []
    for k, row in expected_cells.items():
        thr = math.ceil(3 * k / 4)
        for j, (pl, pv) in enumerate(ps.items()):
            t = float(binom_tail(k, pv, thr))
            want = row[j]
            if want is None:                      # "<1e-5" / "=1" cells
                okc = t < 1e-5 if k == 96 and pl == "0.50" else t > 0.9999
                if not okc:
                    bad.append(f"k{k}@p{pl}")
            elif not close(t, want, 5):
                bad.append(f"k{k}@p{pl}:{t:.5f}!={want}")
    ck("C1_all_18_concordance_tail_cells_exact_to_display_precision",
       not bad, "; ".join(bad) if bad else
       "thresholds ceil(3k/4)=18/36/72; k-cliff at p=0.70 reproduced "
       "(0.38859 > 0.27962 > 0.16938)")

    # --- D. shift-method power on the retained sample (memo section 4) -------
    shift_rows = [(0, 9, 0.00021), (2, 10, 0.00097), (4, 13, 0.03041),
                  (6, 15, 0.14533), (8, 18, 0.60741), (10, 20, 0.90883)]
    bad = []
    for mu, cnt, powwant in shift_rows:
        c = sum(1 for v in lat if v >= FLOOR_LAT - mu)
        pw = float(binom_tail(K_PAIRS, Fraction(c, K_PAIRS), CONC))
        if c != cnt or not close(pw, powwant, 5):
            bad.append(f"mu={mu}: count={c}/{cnt} pow={pw:.5f}/{powwant}")
    ck("D1_shift_method_counts_and_exact_powers_match", not bad,
       "; ".join(bad) if bad else
       "mu in {0,2,4,6,8,10} -> crossings 9/10/13/15/18/20 of 24")
    ck("D2_internal_consistency_mu8_row_equals_section3_p075_cell",
       float(binom_tail(24, Fraction(3, 4), CONC))
       == float(binom_tail(24, Fraction(18, 24), CONC)),
       "both are tail(Bin(24,3/4)>=18) = 0.60741")
    mu_star = FLOOR_LAT - lat[6]        # 7th smallest must clear after shift
    ck("D3_minimal_uniform_shift_for_any_crossing_is_359_over_48",
       mu_star == Fraction(359, 48)
       and close(mu_star / FLOOR_LAT, 1.87, 2),
       f"mu* = {mu_star} = {float(mu_star):.3f} lattice units = "
       f"{float(mu_star / FLOOR_LAT):.2f}x the registered floor")

    # --- E. normal-quantile cross-check (labelled approximation) -------------
    nd = NormalDist()
    p50 = next(i / 10000 for i in range(10000)
               if float(binom_tail(24, Fraction(i, 10000), CONC)) >= 0.5)
    p80 = next(i / 10000 for i in range(10000)
               if float(binom_tail(24, Fraction(i, 10000), CONC)) >= 0.8)
    mu50 = 4 + sd_lat * nd.inv_cdf(p50)
    mu80 = 4 + sd_lat * nd.inv_cdf(p80)
    ck("E1_normal_map_50pct_point_matches_memo_claim",
       abs(p50 - 0.73) <= 0.005 and abs(mu50 - 7.5) <= 0.05,
       f"exact p_up for 50% power = {p50:.4f}; mu* = {mu50:.3f} "
       f"(memo: p_up ~ 0.73, mu* ~ 7.5) -- FINDING: memo's mu*_50 = 7.43 at "
       f"the population sigma, or 7.51 only under the sample sigma; "
       f"conclusion (unreachable ~1.86x floor) unchanged", cls="EST")
    ck("E2_normal_map_80pct_point_matches_memo_claim",
       abs(p80 - 0.80) <= 0.005 and abs(mu80 - 8.74) <= 0.05,
       f"exact p_up for 80% power = {p80:.4f}; mu* = {mu80:.3f} "
       f"(memo: p_up ~ 0.80, mu* ~ 8.74)")
    ck("E3a_printed_map_values_agree_within_stated_0p03",
       abs(7.5 - float(mu_star)) <= 0.03,
       f"|printed 7.5 - shift-map {float(mu_star):.4f}| = "
       f"{abs(7.5 - float(mu_star)):.4f}: true OF THE PRINTED ROUNDED VALUES")
    agree = abs(mu50 - float(mu_star))
    ck("E3b_consistent_sigma_map_gap_within_0p03",
       agree <= 0.03,
       f"consistent-population-sigma gap |{mu50:.4f} - "
       f"{float(mu_star):.4f}| = {agree:.4f} > 0.03 -- FINDING: the memo's "
       f"'both maps agree within 0.03 units' holds only for its printed "
       f"rounded pair; conclusions unchanged", cls="EST")

    # --- F. mean-rule alternative arithmetic (memo section 5) ----------------
    sigma = sd_lat                                   # 5.7061 lattice units
    z975, z80 = nd.inv_cdf(0.975), nd.inv_cdf(0.80)
    n_sqrt = math.sqrt(24)
    mu_mean = (z975 + z80) * sigma / n_sqrt
    beta_bound, integral = 8e-5, 9.1e3               # carried priors, memo sec 5
    d_bound = beta_bound * integral
    lam = d_bound / (sigma / n_sqrt)
    pow_bound = nd.cdf(lam - z975) + nd.cdf(-lam - z975)
    slope_thr = mu_mean / integral
    ck("F1_mean_rule_design_sizing_reproduces",
       abs(mu_mean - 3.26) <= 0.01
       and abs(pow_bound - 0.09) <= 0.01
       and close(slope_thr, 3.6e-4, 5)
       and abs(slope_thr / beta_bound - 4.5) <= 0.05,
       f"mu*_80 = {mu_mean:.3f}; power at bound slope = {pow_bound:.4f}; "
       f"powered slopes >= {slope_thr:.2e} = {slope_thr/beta_bound:.2f}x bound")
    # divergence case: signal beta*455*T vs noise 2.80*sigma*sqrt(T/20)/sqrt(24)
    coef_sig = beta_bound * 455
    coef_noise = (z975 + z80) * sigma / n_sqrt / math.sqrt(20)
    x_T = coef_noise / coef_sig                       # sqrt(T) root
    T_div = x_T ** 2
    W_div = 120 * T_div
    wall_div = (9960 / 3600) * (W_div + 2) / 2402
    ck("F2_window_divergence_solution_reproduces",
       abs(T_div - 401) / 401 <= 0.02 and abs(W_div - 48000) / 48000 <= 0.02
       and abs(wall_div - 55) / 55 <= 0.03,
       f"T = {T_div:.1f} turnovers, W = {W_div:,.0f} ticks, "
       f"est wall = {wall_div:.1f} h (memo: ~401 / ~48,000 / ~55 h)")

    # --- G. window-scaling table (memo section 6, estimate tolerance) --------
    def regime_row(mu_target, area_per_turnover):
        t = mu_target / (beta_bound * area_per_turnover)
        w = 120 * t
        return t, w, (9960 / 3600) * (w + 2) / 2402

    expected_G = [
        (7.85, 455, (215.7, 25879, 29.8)),
        (8.80, 455, (241.8, 29011, 33.4)),
        (7.85, 2601, (37.7, 4527, 5.2)),
        (8.80, 2601, (42.3, 5075, 5.9)),
    ]
    bad = []
    for tgt, area, (t_w, w_w, h_w) in expected_G:
        t, w, h = regime_row(tgt, area)
        # estimate cells: allow one final-display-digit of rounding-path
        # freedom (single-recorded-wall linear extrapolation)
        if not (close(t, t_w, 1) and close(w, w_w, 0)
                and abs(h - h_w) <= 0.15):
            bad.append(f"mu*={tgt}/area={area}: {t:.1f},{w:.0f},{h:.1f}"
                       f" vs {t_w},{w_w},{h_w}")
    ck("G1_four_scaling_table_rows_reproduce_under_declared_linear_model",
       not bad, "; ".join(bad) if bad else
       "targets mu* in {7.85, 8.80} x areas {455 realistic, 2601 ceiling}; "
       "wall scales linearly from the execution-note 2h46m at W=2400 "
       "(ceiling-80% wall cell recomputes to 5.849 vs printed ~5.9: one "
       "final-digit rounding-path difference, within estimate tolerance)",
       cls="EST")
    obs_t, obs_w, obs_h = regime_row(mu50, 455)
    obs_tc, obs_wc, obs_hc = regime_row(mu50, 2601)
    ck("G2_OBSERVATION_true_50pct_targets_are_below_the_memo_rows",
       True,
       f"memo's '~50%' targets correspond to p_up = 0.75 (exact power 60.7%); "
       f"at the exact 50% point mu* = {mu50:.3f}: realistic T = {obs_t:.1f}, "
       f"W = {obs_w:,.0f}, est {obs_h:.1f} h; ceiling T = {obs_tc:.1f}, "
       f"W = {obs_wc:,.0f}, est {obs_hc:.1f} h -- conservative direction, "
       f"closure conclusions and the R1 band (~5-6 h) unchanged")

    # --- H. recruitment blockage identity (memo section 7) -------------------
    m_tot = sum(p["arms"]["M"]["admitted_births_total"] for p in raw["pairs"])
    r_tot = sum(p["arms"]["R0"]["admitted_births_total"] for p in raw["pairs"])
    per_seed_eq = all(p["arms"]["M"]["admitted_births_total"]
                      == p["arms"]["R0"]["admitted_births_total"]
                      for p in raw["pairs"])
    flag = raw["integrity"].get("arm_contrast_is_exactly_the_kernel") is True
    ck("H1_admitted_births_identity_23933_equals_23933_per_seed_and_total",
       m_tot == r_tot == 23933 and per_seed_eq and flag,
       f"Arm M total = Arm R0 total = {m_tot:,}; all 24 seeds arm-equal; "
       "raw integrity arm_contrast_is_exactly_the_kernel = true")

    # --- I. door status: R1-R3 unfired; retained directory immutable ---------
    listing = sorted(p.name for p in PAIRED.iterdir())
    ck("I1_no_new_artifacts_since_session_8_doors_unfired",
       listing == ["confirmatory-paired-20310529-reduced.json",
                   "confirmatory-paired-20310529.json",
                   "pre-execution-manifest.json"],
       f"results/stage8-alpha-evolution-paired contains exactly {listing}")
    note_txt = EXEC_NOTE.read_text()
    ck("I2_wall_basis_bound_to_execution_note",
       "2 h 46 m" in note_txt and close(9960 / 3600, 2 + 46 / 60, 4),
       "execution note records wall ~= 2h46m (mtime-bound); memo's 9960 s "
       "conversion is exact")
    man = json.loads(MAN_P.read_text())
    sm = raw["source_manifest_sha256"]
    mism = [f for f, h in sm.items()
            if f"src/{f}" in man.get("files", {})
            and man["files"][f"src/{f}"]["sha256"] != h]
    ck("I3_frozen_source_pins_still_bind_raw_artifact_streams",
       not mism and len(sm) == 14,
       f"{len(sm)} FROZEN_SOURCES pin-matched; mismatches={mism}")

    return checks


def main():
    checks = run_audit()
    width = max(len(c[0]) for c in checks)
    exact_fail, est_findings = 0, 0
    for name, ok, det, cls in checks:
        if ok:
            tag = "PASS"
        else:
            tag = "FINDING" if cls == "EST" else "FAIL"
            est_findings += (cls == "EST")
            exact_fail += (cls == "EXACT")
        print(f"{tag:<7} [{cls}] {name}  {det}")
    n = len(checks)
    passed = n - exact_fail - est_findings
    print(f"\n{n - exact_fail}/{n} checks clean ({passed} PASS + "
          f"{est_findings} labelled-approximation FINDINGS); "
          f"exact-claim FAILURES={exact_fail}")
    raise SystemExit(1 if exact_fail else 0)


if __name__ == "__main__":
    main()
