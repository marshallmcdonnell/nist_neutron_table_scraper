import periodictable as pt
from typing import Union

argon_isotopes = {
    "Ar": pt.Ar,
    "36Ar": pt.Ar[36],
    "38Ar": pt.Ar[38],
    "40Ar": pt.Ar[40],
}

def get_neutron_info(iso: Union[pt.core.Element, pt.core.Isotope]) -> list[float]:
    # Coherent / incoherent scattering lengths (fm) 
    b_coh = iso.neutron.b_c  # coherent part
    b_inc = None # not sure how to get this from periodictable

    # Cross sections (barns)
    xs_coh = iso.neutron.coherent
    xs_inc = iso.neutron.incoherent
    xs_scat = iso.neutron.total
    xs_abs = iso.neutron.absorption


    return [
        b_coh, b_inc, xs_coh, xs_inc, xs_scat, xs_abs
    ]

argon_data = {}

# Compute isotope-level data
for iso_name, iso in argon_isotopes.items():
    argon_data[iso_name] = get_neutron_info(iso)

# Helper to format table output
def fmt(v):
    if v is None:
        return "      null"
    return f"{v:10.6f}"

def format_row(key, values):
    return f"{key:5} : [ " + ", ".join(fmt(v) for v in values) + " ]"

# Print table
print("# Coh_b(fm) Incoh_b(fm) Coh_xs(b) Incoh_xs(b) Scatt_xs(b) Abs_xs(b)")
for key, value in argon_data.items():
    print(format_row(key, value))
