description = 'Helios 3He analyzer system'
group = 'plugplay'

devices = {
    f'flipper_{setupname}': device('nicos_mlz.devices.helios.HePolarizer',
        description = 'polarization direction of Helios cell with RF flipper',
        tangodevice = f'tango://{setupname}:10000/box/helios/flipper',
    ),
}
