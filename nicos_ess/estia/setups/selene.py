description = 'High-level interface to the Selene Guide components'

includes = ['robot']

display_order = 40 # sort before default devices

devices = dict(
    sr1=device(
        'nicos_ess.estia.devices.selene.SeleneRobot',
        description='Selene 1 Robot',
        position_data='data_artur/selene1_roboit_refined.yaml',
        engaged=0.02, retracted=27.98, delta12=358.7,
        move_x='robot_pos', move_z='robot_vert',
        adjust1='driver1_1_adjust', approach1='driver1_1_approach', hex_state1='driver1_1_hex_state',
        adjust2='driver1_2_adjust', approach2='driver1_2_approach', hex_state2='driver1_2_hex_state',
        unit='Item/Group'
        ),
)
