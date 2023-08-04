# use refined positions and fix an error in mapping of screw locations
sr2.save_data('data_artur/selene2_first_falsemapping.yaml')

pos_remap={}
for item in [2,3]:
    pos_remap[item] = {}
    for group in range(1,16):
        pos_remap[item][group] = sr2.positions[item-1][group]

item = 1
pos_remap[item] = {}
for group in range(1,16):
    pos_remap[item][group] = (sr2.positions[1][group][0], sr2.positions[1][group][1]+35.)

for dx, dz, item in [
    (36.5, 0, 4),
    (36.5, -64, 5),
    (36.5, -170, 6),
    ]:
    pos_remap[item] = {}
    for group in range(1,16):
        
        pos_remap[item][group] = (sr2.positions[1][group][0]+dx, sr2.positions[1][group][1]+dz)

sr2.positions = pos_remap

# run missing screws search
#for item in [1, 4, 5, 6]:
#    for group in range(1, 16):
#        maw(sr2, (item, group))
#        sr2.search_screw(auto_refine=True, auto_update=True)
