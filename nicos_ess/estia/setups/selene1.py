description = 'High-level interface to the Selene Guide components'

includes = ['cart_selene1', 'robot_selene1', 'interferometer']

display_order = 40 # sort before default devices

devices = dict(
    sr1=device(
        'nicos_ess.estia.devices.selene.SeleneRobot',
        description='Selene 1 Robot',
        position_data='data_artur/selene1_robot_active.yaml',
        engaged=0.02, retracted=27.98, delta12=358.7,
        move_x='robot1_pos', move_z='robot1_vert',
        adjust1='driver1_1_adjust', approach1='driver1_1_approach', hex_state1='driver1_1_hex_state',
        adjust2='driver1_2_adjust', approach2='driver1_2_approach', hex_state2='driver1_2_hex_state',
        vertical_screws=(1,2,4),
        unit='Item/Group'
        ),
    sm1=device(
        'nicos_ess.estia.devices.selene.SeleneMetrology',
        description='Selene 1 Metrology', unit='Item/Group',
        m_cart='mcart', interferometer='multiline',
        ch_u_h1='ch19', ch_u_h2='ch20', ch_d_h1='ch23', ch_d_h2='ch24',
        ch_u_v1='ch17', ch_u_v2='ch18', ch_d_v1='ch21', ch_d_v2='ch22',
    )
)
