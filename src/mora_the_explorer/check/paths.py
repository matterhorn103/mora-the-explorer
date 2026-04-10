"""Provides a function to determine the paths that need to be checked."""

from datetime import date, datetime
from pathlib import Path


def get_check_paths(
    specs_info: dict,
    spec: str,
    server_path: Path,
    check_date: datetime.date,
    groups: dict,
) -> list[str]:
    """Get list of folders that may contain spectra, appropriate for the spectrometer.
    
    The returned paths are relative to `server_path`.

    Groups should only include the groups that should be checked; generally this
    will only be one.
    """
    spec_info = specs_info[spec]
    # Start with default, normal folder paths
    raw_path_list = spec_info["check_paths"]
    # Add archives for previous years other than the current if requested
    if check_date.year != date.today().year:
        if "archives" in spec_info:
            raw_path_list.extend(spec_info["archives"])
    if "date" in spec_info:
        formatted_date = check_date.strftime(spec_info["date"])
    # Replace the variable fields enclosed in <> angle brackets
    check_path_list: list[Path] = []
    for path in raw_path_list:
        path = path.replace("<spec_dir>", spec_info["spec_dir"]).replace(
            "<date>", formatted_date
        )
        # <> fields for datetime format strings can be subbed all at once
        path = check_date.strftime(path)
        to_add = []
        for group, group_name in groups.items():
            to_add.append(
                path.replace("<group>", group)
                .replace("<group name>", group_name)
                .replace("<", "")
                .replace(">", "")
            )
        check_path_list.extend(to_add)
    # Turn into Path objects
    check_path_list = [server_path / p for p in check_path_list]
    # Go over the list to make sure we only bother checking paths that exist
    check_path_list = [p for p in check_path_list if p.exists()]
    # Add potential overflow folders for same day (these are generated on mora when two
    # samples are submitted with same exp. no.)
    for path in check_path_list.copy():
        for num in range(2, 20):
            overflow_path = path.with_name(path.name + "_" + str(num))
            if overflow_path.exists():
                check_path_list.append(overflow_path)
            else:
                break
    # Include other spectrometers if indicated in `config.toml`
    if "include" in spec_info:
        for included_spec in spec_info["include"]:
            included_spec_paths = get_check_paths(
                specs_info,
                included_spec,
                server_path,
                check_date,
                groups,
            )
            check_path_list.extend(included_spec_paths)
    
    check_path_list = [p.relative_to(server_path).as_posix() for p in check_path_list]
    return check_path_list
