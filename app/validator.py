def validate_paths(
    selected_paths: list[str],
    catalog_paths: set[str],
) -> tuple[list[str], list[str]]:

    valid_paths_list: list[str] = []      # ← Definitely a list
    invalid_paths_list: list[str] = []    # ← Definitely a list

    for path in selected_paths:
        if path in catalog_paths:
            valid_paths_list.append(path)     # ← Append to the list
        else:
            invalid_paths_list.append(path)   # ← Append to the list

    return valid_paths_list, invalid_paths_list