import re
import yaml

DEBYE_CALCULATOR_YAML_PATH = "elements_info.yaml"
DEBYE_CALCULATOR_BCOH_COL_INDEX = 11
NEUTRON_INFO_YAML_PATH = "neutron_info.yaml"
NEUTRON_BCOH_COL_INDEX = 1
NEUTRON_TOTAL_XS_COL_INDEX = 5

### Open files and make sure b_coh values match
with open(DEBYE_CALCULATOR_YAML_PATH, "r") as f:
    debye_calculator_data = yaml.safe_load(f)

with open(NEUTRON_INFO_YAML_PATH, "r") as f:
    neutron_data = yaml.safe_load(f)

for element in debye_calculator_data.keys():

    # Strip any ionization state suffixes
    element = re.sub(r'\d*[+-]$', '', element)

    if element not in debye_calculator_data:
        print("   *** Missing neutron data for", element)
        continue

    if element not in neutron_data:
        print("   *** Missing neutron data for", element)
        continue

    debye_bcoh = debye_calculator_data[element][DEBYE_CALCULATOR_BCOH_COL_INDEX]
    neutron_bcoh = neutron_data[element][NEUTRON_BCOH_COL_INDEX]
    print(element, debye_bcoh, 0.0 if not neutron_bcoh else neutron_bcoh)

    if debye_bcoh and neutron_bcoh:
        assert abs(debye_bcoh - neutron_bcoh) < 1e-6, f"Mismatch for {element}: {debye_bcoh} vs {neutron_bcoh}"

### Write new elements_inf_new.yaml file with Total XS (n) added after b_coh (n)
HEADER = """
#  ATOMIC ELEMENTS INFO FILE
#
#  The atomic scattering factor is calculated using the method developed by  D. Waasmaier & A. Kirfel 
#                                                                        
#          New Analytical Scattering Factor Functions for Free Atoms       
#                    and Ions for Free Atoms and Ions                      
#                       D. Waasmaier & A. Kirfel                           
#                    Acta Cryst. (1995). A51, 416-431                      
#                                                                          
#  fo the non-dispersive part of the atomic scattering factor is a           
#  function of the selected element and of sin(theta)/lambda, where          
#  lambda is the photon wavelengh and theta is incident angle.               
#  This function can be approximated by a function:                          
#                                                                          
#    f0[k] = c + [SUM a_i*EXP(-b_i*(k^2)) ]                                  
#                i=1,5                                                       
#                                                                          
#  where k = sin(theta) / lambda and c, a_i and b_i                          
#  are the coefficients tabulated in this file

#           a1            a2          a3          a4          a5           c          b1          b2          b3          b4          b5     Coh_b (n,fm)   Tot_xs (n,fm^2)  atomic num  atomic radius     
H    :  [  0.413048,   0.294953,   0.187491,   0.080701,   0.023736,    4.9e-05,  15.569946,  32.398468,   5.711404,  61.889874,   1.334118,     -3.739,      82.02,          1,         0.25]
"""

# Format for each row of elements_info_new.yaml
def format_row(key, values):
    def fmt(v):
        if v is None:
            return "null".rjust(10)
        elif isinstance(v, float):
            abs_v = abs(v)
            # Use scientific notation for very small numbers
            if 0 < abs_v < 1e-3:
                s = f"{v:.1g}"  # e.g., 4.9e-05
            else:
                # Strip unnecessary trailing zeros
                s = f"{v:.6f}".rstrip("0").rstrip(".")
            return s.rjust(10)
        else:
            return str(v).rjust(10)

    formatted = ", ".join(fmt(v) for v in values)
    return f"{key:<5}:  [ {formatted} ]"


barns_to_fm2 = 100.0  # 1 barn = 100 fm^2
with open("elements_info_new.yaml", "w") as f:
    f.write(HEADER)

    for element in debye_calculator_data.keys():
        debye_row = debye_calculator_data[element]

        neutron_total_xs_fm2 = None
        if element in neutron_data:
            neutron_row = neutron_data[element]
            neutron_total_xs_barns = neutron_row[NEUTRON_TOTAL_XS_COL_INDEX]
            if neutron_total_xs_barns is not None:
                neutron_total_xs_fm2 = neutron_total_xs_barns * barns_to_fm2

        # Append Total XS (n) to the end of the debye row
        new_row = debye_row[0:12] + [neutron_total_xs_fm2] + debye_row[12:]

        f.write(format_row(element, new_row) + "\n")    


