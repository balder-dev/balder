from typing import Union


def compare_tree_output_lines(stdout_lines: list[str], expected_output: Union[list, tuple]) -> bool:

    def _check_element(remaining_stdout_lines: list[str], expected_element: Union[list, tuple, str]) -> tuple[list[str], bool]:
        if isinstance(expected_element, str):
            if expected_element == remaining_stdout_lines[0]:
                return remaining_stdout_lines[1:], True
            else:
                return remaining_stdout_lines, False
        elif isinstance(expected_element, list):
            return _check_list(remaining_stdout_lines, expected_element)
        elif isinstance(expected_element, tuple):
            return _check_tuple(remaining_stdout_lines, expected_element)
        else:
            raise TypeError(f"Expected output to be a list or tuple, got {type(expected_output)}")

    def _check_tuple(remaining_stdout_lines: list[str], expected_tuple: tuple) -> tuple[list[str], bool]:
        """tuple means, that order needs to be exact"""
        cur_remaining_stdout_lines = remaining_stdout_lines.copy()
        after_this_element_remaining_stdout_lines = remaining_stdout_lines.copy()
        for tuple_element in expected_tuple:
            after_this_element_remaining_stdout_lines, result = _check_element(cur_remaining_stdout_lines, tuple_element)
            if not result:
                return remaining_stdout_lines, False
            cur_remaining_stdout_lines = after_this_element_remaining_stdout_lines
        return after_this_element_remaining_stdout_lines, True


    def _check_list(remaining_stdout_lines: list[str], expected_list: list) -> tuple[list[str], bool]:
        """list means, that one of the element needs to pass, otherwise it should return False"""
        remaining_stdout_lines = remaining_stdout_lines.copy()
        remaining_expected_list = expected_list.copy()
        while len(remaining_expected_list) > 0:
            result_by_possibility = []

            for element in remaining_expected_list:
                result_by_possibility.append(_check_element(remaining_stdout_lines, element))

            selection = [(rem, res) for rem, res in result_by_possibility if res is True]
            if len(selection) > 1:
                raise ValueError(f'found multiple matches for list: {expected_list} within data {remaining_stdout_lines}')
            if len(selection) == 0:
                return remaining_stdout_lines, False
            remaining_stdout_lines = selection[0][0]
            remaining_expected_list.remove(
                remaining_expected_list[result_by_possibility.index((selection[0]))]
            )
        return remaining_stdout_lines, True

    full_result_remaining, full_result = _check_element(
        remaining_stdout_lines=stdout_lines.copy(),
        expected_element=expected_output.copy()
    )
    if full_result_remaining:
        return False
    return full_result
