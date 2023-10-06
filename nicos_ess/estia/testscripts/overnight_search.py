for item in range(1,7):
    for group in range(1, 16):
        maw(sr2, (item, group))
        sr2.search_screw(auto_refine=True, auto_update=True)
