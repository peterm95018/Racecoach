## Distance Channel Limitation

RaceChrono exported distance appears to be cumulative path distance,
not normalized distance along a fixed course centerline.

Evidence:
- GGLC 2025-11-01
- Lap 4 max distance = 607.22
- Lap 5 max distance = 602.54
- Official time difference = 0.160 sec

Distance-based segment timing currently produces incorrect deltas.

Future solution:
- Reference-path projection
- GPS trace segmentation
- Course markers


