"""NICOS GUI default configuration."""


main_window = docked(
    tabbed(
        ('Experiment', panel('nicos_ess.gui.panels.exp_panel.ExpPanel')),
        ('Setup',
         panel('nicos.clients.flowui.panels.setup_panel.SetupsPanel')),
        ('  ', panel('nicos.clients.flowui.panels.empty.EmptyPanel')),
        (
            'Instrument interaction',
            hsplit(
                vbox(
                    panel(
                        'nicos.clients.flowui.panels.cmdbuilder.CommandPanel',
                        modules=['nicos.clients.gui.cmdlets'],
                    ),
                    vsplit(
                        tabbed(
                            ('Output',
                             panel(
                                 'nicos.clients.flowui.panels.console.ConsolePanel',
                                 hasinput=False)),
                            ('Scan Plot',
                             panel('nicos.clients.flowui.panels.scans.ScansPanel')
                             ),
                            ('Detector Image',
                             panel(
                                 'nicos.clients.flowui.panels.live.MultiLiveDataPanel'
                             )),
                            ('Script Status',
                             panel(
                                 'nicos.clients.flowui.panels.status.ScriptStatusPanel',
                                 eta=True)),
                            ('Selene Sketch',
                             vsplit(
                                 # panel(
                                 #        'nicos_ess.estia.gui.panels.sketchpanel_metrology.MetrologySketchPanel',
                                 #        channels=[
                                 #            # (CHi, pos, diagonal)
                                 #            ('ch17', (-70,  -25), False),
                                 #            ('ch18', (-70,  -70), False),
                                 #            ('ch19', (-70,  100), True),
                                 #            ('ch20', (-70,  180), True),
                                 #
                                 #            ('ch21', (70,  -25), False),
                                 #            ('ch22', (70,  -70), False),
                                 #            ('ch23', (70,  100), True),
                                 #            ('ch24', (70,  180), True),
                                 #            ],
                                 #        positions=['ch27', 'ch28'],
                                 #        offsetx=0,
                                 #     ),
                                 # panel(
                                 #        'nicos_ess.estia.gui.panels.sketchpanel_robot.RobotSketchPanel',
                                 #        posx='robot_pos',
                                 #        posz='robot_vert',
                                 #        approach1='driver1_1_approach',
                                 #        rotation1='driver1_1_adjust',
                                 #        approach2='driver1_2_approach',
                                 #        rotation2='driver1_2_adjust',
                                 #        robot='sr1',
                                 #        offsetx=165.0,
                                 #        offsetz=65.0,
                                 #        deckpos='right',
                                 #        screw_group=[
                                 #                # relative location of screws in each mirror group
                                 #                # (x, z, active, item-1)
                                 #                (50, 234, True, 3),
                                 #                (50, 64, True, 4),
                                 #                (50, 30, True, 5),
                                 #
                                 #                (445, 234, True, 0),
                                 #                (445, 128, True, 1),
                                 #                (445, 64, True, 2),
                                 #                # second guide, not active
                                 #                (50, 500-128, False, -2),
                                 #                (50, 500-64, False, -2),
                                 #                (50, 500-30, False, -2),
                                 #
                                 #                (445, 500-234, False, -2),
                                 #                (445, 500-128, False, -2),
                                 #                (445, 500-64, False, -2),
                                 #                ],
                                 #    ),
                                     panel(
                                             'nicos_ess.estia.gui.panels.sketchpanel_robot.RobotSketchPanel',
                                             selene=2,
                                             posx='robot_pos',
                                             posz='robot_vert',
                                             approach1='driver1_1_approach',
                                             rotation1='driver1_1_adjust',
                                             approach2='driver1_2_approach',
                                             rotation2='driver1_2_adjust',
                                             robot='sr1',
                                             offsetx=165.0,
                                             offsetz=65.0,
                                             deckpos='right',
                                             screw_group=[
                                                 # relative location of screws in each mirror group
                                                 # (x, z, active, item-1)
                                                 (50, 234, True, 3),
                                                 (50, 64, True, 4),
                                                 (50, 30, True, 5),

                                                 (445, 234, True, 0),
                                                 (445, 128, True, 1),
                                                 (445, 64, True, 2),
                                                 # second guide, not active
                                                 (50, 500-128, False, -2),
                                                 (50, 500-64, False, -2),
                                                 (50, 500-30, False, -2),

                                                 (445, 500-234, False, -2),
                                                 (445, 500-128, False, -2),
                                                 (445, 500-64, False, -2),
                                                 ],
                                             ),
                                     panel(
                                             'nicos_ess.estia.gui.panels.sketchpanel_metrology.MetrologySketchPanel',
                                             selene=2,
                                             channels=[
                                                 # (CHi, pos, diagonal)
                                                 ('ch17', (-70,   25), False),
                                                 ('ch18', (-70,   70), False),
                                                 ('ch19', (-70, -100), True),
                                                 ('ch20', (-70, -180), True),

                                                 ('ch21', (70,   25), False),
                                                 ('ch22', (70,   70), False),
                                                 ('ch23', (70, -100), True),
                                                 ('ch24', (70, -180), True),
                                                 ],
                                             positions=['ch27', 'ch28'],
                                             offsetx=0,
                                             ),
                                     ),
                             ),
                            ),
                        ),
                    ),  # vbox
                panel(
                    'nicos.clients.flowui.panels.devices.DevicesPanel',
                    dockpos='right',
                    param_display={'Exp': ['lastpoint', 'lastscan']},
                    filters=[],
                ),
            ),  # hsplit
        ),
        (
            'Batch file generation',
            panel('nicos.clients.flowui.panels.editor.EditorPanel',
                  tools=None),
        ),
        (
            'History',
            panel('nicos.clients.flowui.panels.history.HistoryPanel'),
        ),
        (
            'Logs',
            tabbed(
                ('Errors',
                 panel('nicos.clients.gui.panels.errors.ErrorPanel')),
                ('Log files',
                 panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
            ),
        ),
        position='left',
        margins=(0, 0, 0, 0),
        textpadding=(30, 20),
    ),  # tabbed
)  # docked

windows = []

tools = [
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]

options = {
    'facility': 'ess',
    'mainwindow_class': 'nicos.clients.flowui.mainwindow.MainWindow',
}
