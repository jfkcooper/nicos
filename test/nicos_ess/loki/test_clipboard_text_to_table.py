from nicos_ess.loki.gui.loki_scriptbuilder import \
    extract_table_from_clipboard_text


def test_one_empty_cell():
    clipboard_data = ''
    assert extract_table_from_clipboard_text(clipboard_data) == [['']]


def test_one_non_empty_cell():
    clipboard_data = 'A'
    assert extract_table_from_clipboard_text(clipboard_data) == [['A']]


def test_empty_row():
    clipboard_data = '\t\t'
    assert extract_table_from_clipboard_text(clipboard_data) == [['', '', '']]


def test_non_empty_row():
    clipboard_data = 'A\tB\tC'

    result = extract_table_from_clipboard_text(clipboard_data)

    assert result == [['A', 'B', 'C']]


def test_empty_column():
    clipboard_data = '\n'
    assert extract_table_from_clipboard_text(clipboard_data) == [[''],
                                                                 ['']]


def test_non_empty_column():
    clipboard_data = 'A\nB'
    assert extract_table_from_clipboard_text(clipboard_data) == [['A'],
                                                                 ['B']]


def test_multiple_empty_cells():
    clipboard_data = '\t\n\t'
    assert extract_table_from_clipboard_text(clipboard_data) == [['', ''],
                                                                 ['', '']]


def test_multiple_non_empty_cells():
    clipboard_data = 'A1\tB1\nA2\tB2'
    assert extract_table_from_clipboard_text(clipboard_data) == [['A1', 'B1'],
                                                                 ['A2', 'B2']]


def test_multiple_non_empty_cells_with_excel_encoding():
    # Excel uses \r\n as the line separator
    clipboard_data = 'A1\tB1\r\nA2\tB2'
    assert extract_table_from_clipboard_text(clipboard_data) == [['A1', 'B1'],
                                                                 ['A2', 'B2']]


def test_mix_of_non_empty_cells_and_empty_cells():
    clipboard_data = '\tB1\nA2\t'
    assert extract_table_from_clipboard_text(clipboard_data) == [['', 'B1'],
                                                                 ['A2', '']]


def test_non_empty_cells_surrounded_by_empty_cells():
    clipboard_data = '\t\t\t\n\tB2\tC2\t\n\tB3\tC3\t\r\n\t\t\t'

    result = extract_table_from_clipboard_text(clipboard_data)

    assert result == [['', '', '', ''],
                     ['', 'B2', 'C2', ''],
                     ['', 'B3', 'C3', ''],
                     ['', '', '', '']]
