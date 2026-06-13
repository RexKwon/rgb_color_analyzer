def compare_colors(color_map):

    if not color_map:
        return set(), {}

    all_colors = list(color_map.values())

    common_colors = set.intersection(*all_colors)

    diff_colors = {}

    for file_name, colors in color_map.items():

        diff_colors[file_name] = (
            colors - common_colors
        )

    return common_colors, diff_colors