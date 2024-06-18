"""All UI-independent backend logic for checking the server and copying new spectra."""
import filecmp
import logging
import shutil
import sys
from datetime import date, datetime
from pathlib import Path


def get_check_paths(
        specs_info: dict,
        spec: str,
        server_path: Path,
        check_date: datetime.date,
        groups: dict,
        group: str,
        wild_group: bool = False,
    ):
    """Get list of folders that may contain spectra, appropriate for the spectrometer."""
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
    check_path_list = []
    for path in raw_path_list:
        path = (
            path
            .replace("<spec_dir>", spec_info["spec_dir"])
            .replace("<date>", formatted_date)
        )
        # <> fields for datetime format strings can be subbed all at once
        path = check_date.strftime(path)
        if wild_group is False:
            path = (
                path
                .replace("<group>", group)
                .replace("<group name>", groups[group])
                .replace("<", "")
                .replace(">", "")
            )
            check_path_list.append(path)
        elif wild_group is True:
            wild_check_path_list = []
            for group, group_name in groups.items():
                wild_check_path_list.append(
                        path
                        .replace("<group>", group)
                        .replace("<group name>", group_name)
                        .replace("<", "")
                        .replace(">", "")
                    )
                check_path_list.extend(wild_check_path_list)
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
                group,
                wild_group,
            )
            check_path_list.extend(included_spec_paths)
    return check_path_list


def get_number_spectra(path: Path | None = None, paths: list[Path] | None = None):
    """Get the total number of spectra folders in the given directory or directories.

    We can then use the length of it to measure progress.
    """
    # Can't remember why it was done this way, I guess the hf check used to be done
    # differently to how it is today
    if paths is None:
        n = sum(1 for x in path.iterdir() if x.is_dir())
    else:
        n = 0
        for path in paths:
            n += sum(1 for x in path.iterdir() if x.is_dir())
    return n


def get_metadata_bruker(folder: Path, server_path) -> dict:
    # Extract title and experiment details from title file in spectrum folder
    title_file = folder / "pdata" / "1" / "title"
    with open(title_file, encoding="utf-8") as f:
        title_contents = f.readlines()
    if len(title_contents) < 2:
        logging.info("Title file is empty")
    title = title_contents[0].split()
    details = title_contents[1].split()

    if len(title) >= 3:
        group = title[0]
        if len(title[1]) <= 3:
            initials = title[1]
            sample_info = title[2:]
        else:
            initials = title[1][:3]
            sample_info = [title[1][3:]].extend(title[2:])
    elif len(title) >= 2:
        # Presumably the initials were not separated correctly from the sample number
        group = title[0]
        initials = title[1][:3]
        try:
            sample_info = [title[1][3:]] if title[1][3].isalnum() else [title[1][4:]]
        except IndexError:
            logging.info("No sample name was given when submitting")
            raise IndexError
    else:
        # Title is not even long enough
        logging.info("Title doesn't have enough parts")
        raise IndexError

    metadata = {
        "server_location": str(folder.relative_to(server_path)),
        "group": group,
        "initials": initials,
        "sample_info": sample_info,  # All remaining parts of title
        "experiment": details[0],
        "solvent": details[1],
        "frequency": None,
    }
    return metadata


def get_metadata_agilent(folder: Path, server_path) -> dict:
    # Find out magnet strength, set to initial false value as flag
    magnet_freq = None
    while magnet_freq is None:
        for subfolder in folder.iterdir():
            text_file = subfolder / "text"
            if text_file.exists():
                with open(text_file, encoding="utf-8") as f:
                    spectrum_info = f.readlines()
                    line_with_freq_split = spectrum_info[3].split(",")
                    magnet_freq = line_with_freq_split[0]
        break

    metadata = {
        "server_location": str(folder.relative_to(server_path)),
        "group": None,
        "initials": folder.name[:3],
        "sample_info": [folder.name[3:]],  # A list so as to match the Bruker version
        "experiment": None,
        "solvent": None,
        "frequency": magnet_freq,
    }
    return metadata


def format_name(
    folder,
    metadata,
    inc_group=False,
    inc_init=False,
    inc_solv=False,
    nmrcheck_style=False,
) -> str:
    """Format folder name according to the user's choices."""
    # Format in the style of NMRCheck if requested i.e. using underscores,
    # including initials and spectrometer and date and (spectrometer's) exp no
    # Note that this is legacy
    if nmrcheck_style is True:
        name = "_".join(
            [
                x
                for x in [
                    metadata["initials"],
                    *metadata["sample_info"],
                    folder.parent.name,
                    folder.name,
                ]
                if x is not None
            ]
        )
    else:
        # Include experiment type e.g. proton
        name = "-".join(
            [
                x
                for x in [
                    *metadata["sample_info"],
                    metadata["experiment"],
                ]
                if x is not None
            ]
        )
    # Apply user choices, some only if NMRCheck style wasn't chosen
    if nmrcheck_style is False:
        if inc_init is True and metadata["initials"] is not None:
            name = metadata["initials"] + "-" + name
        if inc_group is True and metadata["group"] is not None:
            name = metadata["group"] + "-" + name
    if inc_solv is True and metadata["solvent"] is not None:
        name = name + "-" + metadata["solvent"]
    # Add frequency info if available
    if metadata["frequency"] is not None:
        name = name + "_" + metadata["frequency"]
    # Make sure there are no special characters in the name, and if so, replace them
    # with the Unicode hexadecimal code points
    # Otherwise Windows will likely reject them
    # Replacing rather than just removing ensures the name is still unique compared to
    # other spectra
    # alphanumeric characters, space, hyphen, underscore are allowed
    allowed_symbols = ["-", "_", " "]
    special = set([x for x in name if not x.isalnum() and x not in allowed_symbols])
    for x in special:
        logging.info(f"Char {x} not permitted in spectrum names, replaced with {str(hex(ord(x)))}")
        name = name.replace(x, str(hex(ord(x))))
    return name


def format_name_admin(
        folder,
        metadata,
        inc_solv=True,
        inc_path=False,
    ) -> str:
    """Format folder name in Klaus' desired fashion."""
    # First do normally but with everything included
    name = format_name(
        folder,
        metadata,
        inc_group=True,
        inc_init=True,
        inc_solv=inc_solv,
    )
    # Add location details if requested
    if inc_path:
        location = metadata["server_location"].replace("/", "_").replace("\\", "_")
        if inc_path == "before" or inc_path is True:
            name = location + "_" + name
        elif inc_path == "after":
            name = name + "_" + location
    return name


def compare_spectra(server_folder, dest_folder) -> int:
    """Check that two spectra with the same name are actually the same measurement and not e.g. different proton measurements.

    In the event that the spectra are the same, a check is made to see if everything has
    been copied; if not, `incomplete` is returned as `True`.
    Result is a tuple with the result in the form `(same, incomplete)`.
    """

    # These are files which can be used to assess if two folders are the same sample
    # On Agilent spectrometers, various files seem to be good candidates for this job
    # but actually often they change after each individual experiment
    diagnostic_files = [
        "fid",  # The actual spectrum
        "audita.txt",  # On Bruker
    ]
    
    # Start with the assumption that they are not the same spectrum/spectra and try
    # to prove otherwise
    same = False
    
    # Compares the list of files between the two directories provided and returns a
    # tuple of three lists (matches, mismatches, errors) - any files not in both
    # directories gets put into errors
    # By setting `shallow = False`, we don't compare metadata but rather the size and
    # content of the files themselves
    top_level_cmp = filecmp.cmpfiles(
        server_folder, dest_folder, diagnostic_files, shallow=False,
    )
    if len(top_level_cmp[0]) > 0:
        same = True
        logging.info(f"Determined to be the same based on {top_level_cmp[0]} being identical")
    
    # If don't seem to be same so far, check any subfolders (which are each spectra
    # on Agilent specs) to see if they are identical spectra
    if not same:
        for x in [x for x in server_folder.iterdir() if x.is_dir()]:
            subdir_cmp = filecmp.cmpfiles(
                x, dest_folder / x.name, diagnostic_files, shallow=False,
            )
            if len(subdir_cmp[0]) > 0:
                same = True
                logging.info(
                    f"Determined to be the same based on {x.name}/{subdir_cmp[0]} being identical"
                )
                # Stop as soon as we find a single hint that they are the same folder
                break
    
    # This compares the contents of the two folders but on metadata only
    comparison = filecmp.dircmp(server_folder, dest_folder)
    
    # One final check
    # This compares just the metadata of any top-level files including modified time,
    # which means even the same spectra might give a false negative, so we can't use it
    # as the main test, but it is unlikely to give a false positive
    if not same:
        if len(comparison.same_files) > 0:
            same = True
            logging.info(
                f"Determined to be the same based on the metadata of {comparison.same_files} being identical"
            )
        
    if same:
        # See if there are any subdirectories or files that we are missing
        # Note that this doesn't look within subfolders
        if len(comparison.left_only) > 0:
            incomplete = True
            logging.info(f"but {comparison.left_only} are missing in copied folder")
        else:
            incomplete = False
    else:
        logging.info("The folders are for different measurements/samples")
        incomplete = False

    return same, incomplete


def copy_folder(src: Path, target: Path):
    """Copy a spectra folder over to the target if it isn't already there.

    Note that `target` should be the target path of the copied folder, not a directory
    to copy it into.

    Should the target already exist, it is assessed whether the folder at the target is
    indeed the same spectrum/spectra or if it just has the same name.

    If the latter is the case, it is copied with a number appended to the name.

    Partial copies are also checked for and recopied if they are incomplete.
    """

    output = []

    # Check that spectrum hasn't been copied before
    same_spectrum_found = False
    incomplete_copy = False
    if target.exists():
        logging.info("Spectrum with this name exists in destination")
        # Check that the spectra are actually identical and not e.g. different
        # proton measurements
        # If confirmed to be unique spectra, need to extend spectrum name with
        # -2, -3 etc. to avoid conflict with spectra already in dest
        same_spectrum_found, incomplete_copy = compare_spectra(src, target)
        num = 1
        while not same_spectrum_found:
            num += 1
            target = target.with_name(target.name + "-" + str(num))
            if target.exists():
                same_spectrum_found, incomplete_copy = compare_spectra(src, target)
            else:
                # We have exhausted all possible candidates for the same spectrum
                # and have arrived at a new unique name, so we need to copy the
                # spectrum and use this unique name
                break

    # Try and fix only partially copied spectra
    if same_spectrum_found is True and incomplete_copy is True:
        logging.info("The existing copy is only partial")
        for x in src.iterdir():
            # Copy any file or subdirectory that isn't already in destination
            if not (target / x.name).exists():
                try:
                    if x.is_dir():
                        shutil.copytree(x, target / x.name)
                    elif x.is_file():
                        shutil.copy2(x, target / x.name)
                except PermissionError:
                    output.append(
                        "You do not have permission to write to the given folder"
                    )
                    return output
        text_to_add = "New files found for: " + target.name
        output.append(text_to_add)

    elif same_spectrum_found is False:
        try:
            shutil.copytree(src, target)
        except PermissionError:
            output.append("You do not have permission to write to the given folder")
            logging.info("No write permission for destination")
            return output
        text_to_add = "Spectrum found: " + target.name
        logging.info(f"Spectrum saved to {target.name}")
        output.append(text_to_add)

    return output


def iterate_progress(prog_state, n, progress_callback):
    """Update progress state and signal to progress bar if a callback object has been given"""
    prog_state += n
    if progress_callback is not None:
        progress_callback.emit(prog_state)
    else:
        print(f"Spectra checked: {prog_state}")
    return prog_state

cache = tuple()
cached_paths = []

def check_nmr(
    fed_options: dict,
    server_path: Path,
    specs_info: dict,
    check_date: datetime.date,
    groups: dict,
    wild_group: bool,
    prog_bar=None,
    progress_callback=None,
    status_callback=None,
):
    """Main checking function for Mora the Explorer."""

    if status_callback is not None:
        status_callback.emit("preparing...")
    
    # Some initial setup that is the same for all spectrometers
    logging.info(f"Beginning check of {check_date} with the options:")
    logging.info(fed_options)
    # Initialize list that will be returned as output
    output_list = ["No new spectra"]
    # Confirm destination directory exists
    if Path(fed_options["dest_path"]).exists() is False:
        logging.info("Given destination folder not found!")
        output_list.append("Given destination folder not found!")
        return output_list
    # Confirm server can be reached
    if server_path.exists() is False:
        logging.info("The NMR server could not be reached!")
        output_list.append("The NMR server could not be reached!")
        return output_list
    spectrometer = fed_options["spec"]
    spec_info = specs_info[spectrometer]

    # Directory discovery
    check_path_list = get_check_paths(
        specs_info,
        spectrometer,
        server_path,
        check_date,
        groups=groups,
        group=fed_options["group"],
        wild_group=wild_group,
    )

    # Give message if no directories for the given date exist yet
    if len(check_path_list) == 0:
        logging.info("No folders exist for this date!")
        output_list.append("No folders exist for this date!")
        return output_list
    else:
        logging.info("The following paths will be checked for spectra:")
        logging.info(check_path_list)

    # Initialize progress bar
    prog_state = 0
    n_spectra = get_number_spectra(paths=check_path_list)
    logging.info(f"Total spectra in these paths: {n_spectra}")
    if prog_bar is not None:
        try:
            prog_bar.setMaximum(n_spectra)
            if progress_callback is not None:
                progress_callback.emit(0)  # Reset bar to 0
            else:
                print(f"Total spectra to check: {n_spectra}")
        except Exception:
            # This stops Python from hanging when the program is closed, no idea why
            sys.exit()
    
    if status_callback is not None:
        status_callback.emit("checking...")

    # Now we have a list of directories to check, start the actual search process
    # Needs to be slightly different depending on the spectrometer, as the contents of
    # the folder for a spectrum is manufacturer-dependent

    logging.info("The following spectra were checked for potential matches:")
    # Loop through each folder in check_path_list
    for check_path in check_path_list:
        # Iterate through spectra
        for folder in check_path.iterdir():
            logging.info(folder)
            
            hit = False
            
            # Extract title and experiment details from title file in spectrum folder
            try:
                if spec_info["manufacturer"] == "bruker":
                    metadata = get_metadata_bruker(folder, server_path)
                elif spec_info["manufacturer"] == "agilent":
                    # Save a step by not extracting metadata unless initials in folder
                    # name as folders are given the name of the sample on Agilent specs
                    if fed_options["initials"] in folder.name:
                        hit = True
                        metadata = get_metadata_agilent(folder, server_path)
                    else:
                        prog_state = iterate_progress(prog_state, 1, progress_callback)
                        continue
                else:
                    raise ValueError(
                        f"Manufacturer {spec_info["manufacturer"]} is not supported!"
                    )
            except FileNotFoundError:
                output_list.append(f"No metadata could be found for {folder}!")
                logging.info("No metadata found")
                prog_state = iterate_progress(prog_state, 1, progress_callback)
                continue
            except IndexError:  # Due to title not being long enough
                prog_state = iterate_progress(prog_state, 1, progress_callback)
                continue

            # Look for search string
            if metadata["initials"] == fed_options["initials"]:
                hit = True
            # Klaus can give a group initialism as the initials and download all spectra
            # from a group
            elif (
                fed_options["group"] == "nmr"
                and metadata["group"] == fed_options["initials"]
            ):
                hit = True

            if not hit:
                # Update progress bar
                prog_state = iterate_progress(prog_state, 1, progress_callback)
                continue
            else:
                logging.info("Spectrum matches search query!")

            # Formatting
            if fed_options["group"] == "nmr":
                new_folder_name = format_name_admin(
                    folder,
                    metadata,
                    inc_solv=fed_options["inc_solv"],
                    inc_path=fed_options["inc_path"],
                )
            else:
                new_folder_name = format_name(
                    folder,
                    metadata,
                    inc_init=fed_options["inc_init"],
                    inc_solv=fed_options["inc_solv"],
                    nmrcheck_style=fed_options["nmrcheck_style"],
                )

            # Copy, add output messages to main output list
            if status_callback is not None:
                status_callback.emit("copying...")
            output_list.extend(
                copy_folder(folder, Path(fed_options["dest_path"]) / new_folder_name)
            )
            if status_callback is not None:
                status_callback.emit("checking...")

            # Update progress bar if a callback object has been given
            # Make sure there's a noticeable movement after copying a spectrum,
            # otherwise it looks frozen
            if prog_bar is not None:
                prog_bar.setMaximum(prog_bar.maximum() + 5)
                prog_state = iterate_progress(prog_state, 5, progress_callback)

    now = datetime.now().strftime("%H:%M:%S")
    completed_statement = f"Check of {check_date} completed at " + now
    output_list.append(completed_statement)
    logging.info(completed_statement)
    return output_list
