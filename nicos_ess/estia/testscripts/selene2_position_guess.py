found_12_x = 315.
found_12_z = 374.66

pos_guess={}
for dx, dz, item in [
    (0, 64, 1),
    (0, 0, 2),
    (0, -106, 3),
    (36.5, 64+35, 4),
    (36.5, 64, 5),
    (36.5, 0, 6),
    ]:
    pos_guess[item]={}
    for group in range(15):
        pos_guess[item][group+1] = (found_12_x+dx+480*group, found_12_z+dz)