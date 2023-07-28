sorted_ulV=[]
sorted_ulH=[]
for item in [1,2,4]:
    for group in range(1,16):
        if group in upper_limits and item in upper_limits[group]:            
            sorted_ulV.append([group, item, upper_limits[group][item]])
        else:
            print(f'missing {item},{group}')
for item in [2,5,6]:
    for group in range(1,16):
        if group in upper_limits and item in upper_limits[group]:            
            sorted_ulH.append([group, item, upper_limits[group][item]])
        else:
            print(f'missing {item},{group}')
sorted_ulV=np.array(sorted_ulV)
sorted_ulV=sorted_ulV[sorted_ulV[:,2].argsort(), :]
sorted_ulH=np.array(sorted_ulH)
sorted_ulH=sorted_ulH[sorted_ulH[:,2].argsort(), :]

with open('data_artur/upper_limit_sorted.dat', 'w') as fh:
    fh.write("### Vertical Adjusters\n")
    fh.write('# group screw u_limit\n')
    for group, item, value in sorted_ulV:
        fh.write(f'{group:02.0f} {item:.0f} {value:8.1f}\n')
    fh.write("### Horizontal Adjusters\n")
    fh.write('# group screw u_limit\n')
    for group, item, value in sorted_ulH:
        fh.write(f'{group:02.0f} {item:.0f} {value:12.1f}\n')
    