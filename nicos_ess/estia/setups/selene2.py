description = 'High-level interface to the Selene Guide components'

includes = ['cart_selene2', 'robot_selene2', 'interferometer']

display_order = 40 # sort before default devices

devices = dict(
    sr2=device(
        'nicos_ess.estia.devices.selene.SeleneRobot',
        description='Selene 2 Robot',
        position_data='data_artur/selene2_robot_active.yaml',
        engaged=-0.02, retracted=-27.98, delta12=358.7,
        move_x='robot2_pos', move_z='robot2_vert',
        adjust1='driver2_2_adjust', approach1='driver2_2_approach', hex_state1='driver2_2_hex_state',
        adjust2='driver2_1_adjust', approach2='driver2_1_approach', hex_state2='driver2_1_hex_state',
        vertical_screws=(3,5,6),
        unit='Item/Group'
    ),
    sm2=device(
        'nicos_ess.estia.devices.selene.SeleneMetrology',
        description='Selene 2 Metrology', unit='Item/Group',
        m_cart='mcart2', interferometer='multiline',
        ch_u_h1='ch19', ch_u_h2='ch20', ch_d_h1='ch23', ch_d_h2='ch24',
        ch_u_v1='ch17', ch_u_v2='ch18', ch_d_v1='ch21', ch_d_v2='ch22',
    )
)
