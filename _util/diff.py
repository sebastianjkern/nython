def diff_dict(d1: dict, d2: dict) -> dict:
    """
    Return a dictionary of differences between two dictionaries.

    Each key present in either `d1` or `d2` is compared. If the values differ,
    the result contains that key mapping to a tuple `(value_in_d1, value_in_d2)`.
    Keys only present in one dictionary have `None` for the missing side.
    """
    differences: dict = {}
    all_keys = set(d1.keys()) | set(d2.keys())
    for key in all_keys:
        val1 = d1.get(key)
        val2 = d2.get(key)
        if val1 != val2:
            differences[key] = (val1, val2)
    return differences
