from pyne import data, nucname
import math

FOUR_PI = 4.0 * math.pi

def fmt(v):
    if v is None:
        return f"{'null':>10}"
    return f"{v:10.6f}"

def format_row(key, values):
    return f"{key:5} : [ " + ", ".join(fmt(v) for v in values) + " ]"

def argon_rows():
    rows = []

    # Element-level row (average over isotopes)
    rows.append((
        "Ar",
        [None, None, None, None, None, None, None]
    ))

    for A in (36, 38, 40):
        nuc = nucname.id(f"Ar{A}")

        abundance = data.natural_abund(nuc) * 100.0

        # Scattering lengths
        b_coh = data.b_coherent(nuc)
        b_inc = data.b_incoherent(nuc)

        xs_coh = FOUR_PI * b_coh**2 if b_coh is not None else None
        xs_inc = FOUR_PI * b_inc**2 if b_inc is not None else None
        xs_scat = xs_coh + xs_inc if xs_coh and xs_inc else None

        # Absorption cross section (thermal) with fallback
        try:
            xs_abs = data.simple_xs(nuc, 'absorption', 'thermal')
        except RuntimeError:
            xs_abs = None

        rows.append((
            f"{A}Ar",
            [abundance, b_coh, b_inc, xs_coh, xs_inc, xs_scat, xs_abs]
        ))

    return rows

# Print result
print("# abundance Coh_b(fm) Incoh_b(fm) Coh_xs(b) Incoh_xs(b) Scatt_xs(b) Abs_xs(b)")
for key, values in argon_rows():
    print(format_row(key, values))
