from typing import Dict


def _compare_observed_entry(original_item: Dict, expected_item: Dict):
    """helper method that helps to compare the original with the expected entry"""
    KEY_FILE = "file"
    KEY_CLS = "cls"
    KEY_METH = "meth"
    KEY_MSG = "msg"
    KEY_CATEGORY = "category"
    KEY_PART = "part"

    ALL_POSSIBLE_KEYS = [KEY_FILE, KEY_CLS, KEY_METH, KEY_MSG, KEY_CATEGORY, KEY_PART]

    if KEY_FILE in expected_item.keys():
        if isinstance(expected_item[KEY_FILE], str) and \
                str(original_item[KEY_FILE]) != expected_item[KEY_FILE]:
            return False
    if KEY_CLS in expected_item.keys():
        if isinstance(expected_item[KEY_CLS], str) and original_item[KEY_CLS] is not None and \
                original_item[KEY_CLS] != expected_item[KEY_CLS]:
            return False
    if KEY_METH in expected_item.keys():
        if isinstance(expected_item[KEY_METH], str) and \
                original_item[KEY_METH] != expected_item[KEY_METH]:
            return False
    if KEY_MSG in expected_item.keys():
        if original_item[KEY_MSG] != expected_item[KEY_MSG]:
            return False
    if KEY_CATEGORY in expected_item.keys():
        if original_item[KEY_CATEGORY] != expected_item[KEY_CATEGORY]:
            return False
    if KEY_PART in expected_item.keys():
        if original_item[KEY_PART] != expected_item[KEY_PART]:
            return False
    for cur_key in expected_item.keys():
        if cur_key not in ALL_POSSIBLE_KEYS:
            raise KeyError(f"unknown key `{cur_key}` was given for expected_data entry dictionary")
    return True


def compare_observed_list_with_expected(observer_list, expected):
    """
    This function checks if the expected elements are given in the observer list. For this the method searches for the
    keys `file`, `cls`, `meth`, `msg`, `category` and `part`. It only checks the keys that are given in the
    dictionaries of the `expected_dict`.

    .. note::
        * LIST: means that the order of the elements does not matter
        * TUPLE: means that all elements in the tuple has to have the given order of the tuple
        * DICT: describes one object

        But note, that every element that exists in the `expected_tuple` has to be in the `observer_list`

    :param observer_list: the real observer list with the data

    :param expected: the expected data with information about the allowed order (List, Tuple, Dict)
    """
    # contains the index of the current observer item, that should be searched in `expected`
    cur_observer_idx = 0

    def go_through_tuple(of_tuple):
        """helps to go through a tuple -> returns False if there is no correct matching anymore otherwise it returns
        True (and updates the `cur_observer_idx`) after the whole tuple was checked"""
        nonlocal cur_observer_idx
        # in this case everything has to be in the exact order as the order given in the tuple
        for cur_tuple_item in of_tuple:
            if isinstance(cur_tuple_item, dict):
                # normal entry
                if _compare_observed_entry(original_item=observer_list[cur_observer_idx], expected_item=cur_tuple_item):
                    cur_observer_idx += 1
                else:
                    return False
            elif isinstance(cur_tuple_item, tuple):
                inner_result = go_through_tuple(cur_tuple_item)
                if not inner_result:
                    return False
            elif isinstance(cur_tuple_item, list):
                inner_result = go_through_list(cur_tuple_item)
                if not inner_result:
                    return False
            else:
                raise TypeError(f"unknown type `{type(cur_tuple_item)}`")
        return True

    def go_through_list(of_list):
        """helps to go through a list -> returns False if there is no correct matching anymore otherwise it returns
           True (and updates the `cur_observer_idx`) after the whole tuple was checked"""
        nonlocal cur_observer_idx
        leftover_items = of_list.copy()

        while len(leftover_items) > 0:
            length_before = len(leftover_items)
            idx_before = cur_observer_idx
            for cur_item in leftover_items:
                if isinstance(cur_item, dict):
                    # normal entry
                    if _compare_observed_entry(original_item=observer_list[cur_observer_idx],
                                               expected_item=cur_item):
                        cur_observer_idx += 1
                        leftover_items.remove(cur_item)
                        break
                elif isinstance(cur_item, tuple):
                    inner_result = go_through_tuple(cur_item)
                    if inner_result:
                        leftover_items.remove(cur_item)
                        break
                    else:
                        # revert index
                        cur_observer_idx = idx_before

                elif isinstance(cur_item, list):
                    inner_result = go_through_list(cur_item)
                    if inner_result:
                        leftover_items.remove(cur_item)
                        break
                    else:
                        # revert index
                        cur_observer_idx = idx_before
            if length_before == len(leftover_items):
                # can not resolve the whole list
                return False
        return True

    if isinstance(expected, tuple):
        result = go_through_tuple(expected)
    elif isinstance(expected, list):
        result = go_through_list(expected)
    else:
        raise TypeError(f"unknown type `{type(expected)}` given for the expected list")

    if not result:
        raise AssertionError(
            f"the execution was not as expected - problem to find the expected in the real data since index "
            f"`{cur_observer_idx}`")
