import copy
import numpy as np
import pytest

from nicos_ess.loki.gui.loki_scriptbuilder_model import LokiScriptModel


NUM_ROWS = 20

HEADERS = ["COLUMN_1", "COLUMN_2", "COLUMN_3",
           "COLUMN_4", "COLUMN_5", "COLUMN_6"]

DATA = [["00", "01", "02", "03", "04", "05"],
        ["10", "11", "12", "13", "14", "15"],
        ["20", "21", "22", "23", "24", "25"],
        ["30", "31", "32", "33", "34", "35"],
        ["40", "41", "42", "43", "44", "45"]]

CLIPBOARD_DATA = [["a", "b", "c",],
                  ["e", "f", "g",],
                  ["i", "j", "k",]]


class TestLokiScriptModel:

    @pytest.fixture(autouse=True)
    def prepare(self):
        self.model = LokiScriptModel(HEADERS, NUM_ROWS)
        self.model.table_data = copy.deepcopy(DATA)

    def test_initialization_done_correctly(self):
        # check shape of the table_data
        assert len(self.model.table_data) == NUM_ROWS
        assert all(
            [len(data) == len(HEADERS) for data in self.model.table_data])

    def test_row_inserted_at_position(self):
        position = 2
        self.model.insertRow(position)
        assert len(self.model.table_data) == NUM_ROWS + 1

        assert self.model.table_data[position-1] == DATA[position-1]
        assert self.model.table_data[position] == [""] * len(HEADERS)
        assert self.model.table_data[position+1] == DATA[position]

    def test_row_removed_at_position(self):
        position = 2
        self.model.removeRows([position])
        assert len(self.model.table_data) == NUM_ROWS - 1
        assert self.model.table_data[position] == DATA[position+1]

        # Remove multiple rows at once
        positions = [4, 5, 6]
        self.model.removeRows(positions)
        assert len(self.model.table_data) == NUM_ROWS - 1 - len(positions)

    def test_data_selected_for_selected_indices(self):
        selected_indices = [(0, 0), (0, 1), (0, 2),
                            (1, 0), (1, 1), (1, 2)]
        selected_data = self.model.select_data(selected_indices)
        assert selected_data == ["\t".join(DATA[0][:3]),
                                 "\t".join(DATA[1][:3])]

    def test_extra_rows_created_when_clipboard_data_pasted_at_bottom_row(self):
        bottom_left = (NUM_ROWS - 1, 0)
        self.model.update_data_from_clipboard(
            copy.deepcopy(CLIPBOARD_DATA), bottom_left)

        assert len(self.model.table_data) == NUM_ROWS + len(CLIPBOARD_DATA) - 1

    # TODO: Improve everything from here (Pairing)
    def test_clipboard_data_gets_pasted_correctly_at_top_right(self):
        top_right = (0, len(HEADERS)-1)
        self.model.update_data_from_clipboard(
            copy.deepcopy(CLIPBOARD_DATA), top_right)

        table_data_np = np.array(self.model.table_data, dtype=np.str_)
        clipboard_data_np = np.array(CLIPBOARD_DATA, dtype=np.str_)

        clip_shape = clipboard_data_np.shape
        table_shape = table_data_np.shape

        row_slice = np.s_[top_right[0]:top_right[0]+clip_shape[0]]
        # Only one column of clip data should be pasted
        np.testing.assert_array_equal(
            table_data_np[row_slice, top_right[1]],
            clipboard_data_np[:,0]
            )
        return table_shape

    def test_clipboard_data_gets_pasted_correctly_at_top_left(self):
        top_left = (0, 0)
        self.model.update_data_from_clipboard(
            copy.deepcopy(CLIPBOARD_DATA), top_left)

        # Convert to numpy arrays for easy slicing
        table_data_np = np.array(self.model.table_data, dtype=np.str_)
        clipboard_data_np = np.array(CLIPBOARD_DATA, dtype=np.str_)

        clip_shape = clipboard_data_np.shape
        table_shape = table_data_np.shape

        row_slice = np.s_[top_left[0]:top_left[0]+clip_shape[0]]
        col_slice = np.s_[top_left[1]:top_left[1]+clip_shape[1]]
        np.testing.assert_array_equal(
            table_data_np[row_slice, col_slice],
            clipboard_data_np
            )

    def test_clipboard_data_gets_pasted_in_table_with_hidden_columns(self):
        hidden_columns = [1]
        top_left = (0, 0)

        self.model.update_data_from_clipboard(
            copy.deepcopy(CLIPBOARD_DATA),
            top_left,
            hidden_columns=hidden_columns)

        # Convert to numpy arrays for easy slicing
        table_data_np = np.array(self.model.table_data, dtype=np.str_)
        clipboard_data_np = np.array(CLIPBOARD_DATA, dtype=np.str_)

        clip_shape = clipboard_data_np.shape
        table_shape = table_data_np.shape

        row_slice = np.s_[top_left[0]:top_left[0]+clip_shape[0]]

        np.testing.assert_array_equal(
            table_data_np[row_slice, hidden_columns],
            np.array(DATA, dtype=np.str_)[row_slice, hidden_columns]
        )
