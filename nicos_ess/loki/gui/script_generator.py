from enum import Enum


class TransOrder(Enum):
    TRANSFIRST = 0
    SANSFIRST = 1
    TRANSTHENSANS = 2
    SANSTHENTRANS = 3
    SIMULTANEOUS = 4


def _get_position(value):
    return f"set_position({value})"


def _get_sample(name, thickness):
    return f"set_sample('{name}', {thickness})"


def _do_trans(row_values, trans_duration_type):
    template = (
        f"# Sample = {row_values['sample']}\n"
        f"{_get_sample(row_values['sample'], row_values['thickness'])}\n"
        f"{_get_position(row_values['position'])}\n"
        f"do_trans({row_values['trans_duration']}, "
        f"'{trans_duration_type}')\n")
    return template


def _do_sans(row_values, sans_duration_type):
    template = (
        f"# Sample = {row_values['sample']}\n"
        f"{_get_sample(row_values['sample'], row_values['thickness'])}\n"
        f"{_get_position(row_values['position'])}\n"
        f"do_sans({row_values['sans_duration']}, "
        f"'{sans_duration_type}')\n")
    return template


def _do_simultaneous(row_values, sans_duration_type):
    template = (
        f"# Sample = {row_values['sample']}\n"
        f"{_get_sample(row_values['sample'], row_values['thickness'])}\n"
        f"{_get_position(row_values['position'])}\n"
        f"do_sans_simultaneous({row_values['sans_duration']}, "
        f"'{sans_duration_type}')\n")
    return template


class TransFirst:
    def generate_script(self, labeled_data, trans_duration_type,
                        sans_duration_type):
        template = ""
        for row_values in labeled_data:
            template += _do_trans(row_values, trans_duration_type)
            template += "\n"

        for row_values in labeled_data:
            template += _do_sans(row_values, sans_duration_type)
            template += "\n"
        return template


class SansFirst:
    def generate_script(self, labeled_data, trans_duration_type,
                        sans_duration_type):
        template = ""
        for row_values in labeled_data:
            template += _do_sans(row_values, sans_duration_type)
            template += "\n"

        for row_values in labeled_data:
            template += _do_trans(row_values, trans_duration_type)
            template += "\n"
        return template


class TransThenSans:
    def generate_script(self, labeled_data, trans_duration_type,
                        sans_duration_type):
        template = ""
        for row_values in labeled_data:
            template += _do_trans(row_values, trans_duration_type)
            template += _do_sans(row_values, sans_duration_type)
            template += "\n"
        return template


class SansThenTrans:
    def generate_script(self, labeled_data, trans_duration_type,
                        sans_duration_type):
        template = ""
        for row_values in labeled_data:
            template += _do_sans(row_values, sans_duration_type)
            template += _do_trans(row_values, trans_duration_type)
            template += "\n"
        return template


class Simultaneous:
    def generate_script(self, labeled_data, trans_duration_type,
                        sans_duration_type):
        template = ""
        for row_values in labeled_data:
            template += _do_simultaneous(row_values, sans_duration_type)
            template += "\n"
        return template


class ScriptGenerator:
    @classmethod
    def from_trans_order(cls, trans_order):
        if trans_order == TransOrder.TRANSFIRST:
            return TransFirst()
        elif trans_order == TransOrder.SANSFIRST:
            return SansFirst()
        elif trans_order == TransOrder.TRANSTHENSANS:
            return TransThenSans()
        elif trans_order == TransOrder.SANSTHENTRANS:
            return SansThenTrans()
        elif trans_order == TransOrder.SIMULTANEOUS:
            return Simultaneous()
        else:
            raise NotImplementedError(
                f"Unspecified trans order {trans_order.name}")
