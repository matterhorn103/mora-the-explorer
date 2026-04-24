"""Provides a function to determine the paths that need to be checked."""

import datetime
from pathlib import Path

from .spec import Spectrometer


def get_check_paths(
    spec_info: Spectrometer,
    server_path: Path,
    check_date: datetime.date,
    groups: dict[str, str],
) -> list[Path]:
    """Get list of folders that may contain spectra, appropriate for the spectrometer.

    Groups should only include the groups that should be checked; generally this
    will only be one.
    """
    # Start with default, normal folder paths
    raw_path_list = spec_info.check_paths
    # Add archives for previous years other than the current if requested
    if check_date.year != datetime.date.today().year:
        raw_path_list.extend(spec_info.archives)
    # Replace the variable fields enclosed in <> angle brackets
    check_path_list: list[Path] = []
    for path in raw_path_list:
        # {} fields for datetime format strings can be subbed all at once
        path = check_date.strftime(path).replace("{", "").replace("}", "")
        to_add = []
        for group, group_name in groups.items():
            to_add.append(path.replace("<group>", group).replace("<group_name>", group_name))
        check_path_list.extend(to_add)

    # Turn into Path objects
    check_path_list = [server_path / p for p in check_path_list]
    # Go over the list to make sure we only bother checking paths that exist
    # check_path_list = [p for p in check_path_list if p.exists()]

    # Include other spectrometers if indicated
    for included_spec in spec_info.include:
        included_spec_paths = get_check_paths(
            included_spec,
            server_path,
            check_date,
            groups,
        )
        check_path_list.extend(included_spec_paths)

    return check_path_list
