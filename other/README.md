# Development stuff

These were other options to try and use packages to get the data instead of scraping website.

```
#            abundance Coh_b (n)    Incoh_b (n) Coh_xs (n) Incoh_xs (n) Scatt_xs (n) Abs_xs (n) 
Ar    : [       null,   1.909000,       null,   0.458000,   0.225000,   0.683000,   0.675000 ]
36Ar  : [   0.337000,  24.900000,   0.000000,  77.900000,   0.000000,  77.900000,   5.200000 ]
38Ar  : [   0.063000,   3.500000,   0.000000,   1.500000,   0.000000,   1.500000,   0.800000 ]
40Ar  : [  99.600000,   1.830000,   0.000000,   0.421000,   0.000000,   0.421000,   0.660000 ]
```

## Argon target table

I use Argon for a test table.

Here is what I pulled from NIST tables using my scraping code.


## periodictable - works but missing incoherent scattering length

The current code using periodictable looks promising but cannot get the b_incoh  yet and no abudance.

Example below shows all but the 40Ar Coh_b match NIST tables above.
```
#           Coh_b(fm)   Incoh_b(fm) Coh_xs(b)   Incoh_xs(b) Scatt_xs(b) Abs_xs(b)
Ar    : [   1.909000,       null,   0.458000,   0.225000,   0.683000,   0.675000 ]
36Ar  : [  24.900000,       null,  77.900000,   0.000000,  77.900000,   5.200000 ]
38Ar  : [   3.500000,       null,   1.500000,   0.000000,   1.500000,   0.800000 ]
40Ar  : [   1.700000,       null,   0.421000,   0.000000,   0.421000,   0.660000 ]
```

## PyNE - doesn't work

Tried to use PyNE with code included here but doesn't have the experimental values
NIST tables do.

Example for Argon output:
```
Ar    : [       null,       null,       null,       null,       null,       null,       null ]
36Ar  : [   0.333600, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j,       null,       null ]
38Ar  : [   0.062900, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j,       null,       null ]
40Ar  : [  99.603500, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j, 0.000000+0.000000j,       null,   0.660000 ]
```

NOTE: Used thne `pyne/ubuntu_18.04_py3` docker hub container image since PyNE is not availalbe via PyPI.