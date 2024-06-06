import filecmp
import logging
import shutil
import sys
from datetime import date, datetime
from pathlib import Path


def get_300er_paths(spec_paths, check_day):
    # Start with default, normal folder path
    check_path_list = [spec_paths["300er"] / check_day]
    # Add archives for previous years other than the current if requested
    year = int(check_day[-4:])
    if year != date.today().year:
        check_path_list.append(
            spec_paths["300er"] / f"{str(year)[-2:]}-av300_{year}" / check_day
        )
    # Account for different structure in 2019/start of 2020
    if year <= 2020:
        check_path_list.append(
            spec_paths["300er"] / f"{str(year)[-2:]}-dpx300_{year}" / check_day
        )
    return check_path_list


def get_400er_paths(spec_paths, check_day):
    check_day_a = "neo400a_" + check_day
    check_day_b = "neo400b_" + check_day
    check_day_c = "neo400c_" + check_day
    # Start with default, normal folder paths
    check_path_list = [
        spec_paths["400er"] / check_day_a,
        spec_paths["400er"] / check_day_b,
        spec_paths["400er"] / check_day_c,
        spec_paths["300er"] / check_day,
    ]
    # Add archives for previous years other than the current if requested
    year = int(check_day[-4:])
    if year != date.today().year:
        check_path_list.extend(
            [
                spec_paths["400er"] / f"{str(year)[-2:]}-neo400a_{year}" / check_day_a,
                spec_paths["400er"] / f"{str(year)[-2:]}-neo400b_{year}" / check_day_b,
                spec_paths["400er"] / f"{str(year)[-2:]}-neo400c_{year}" / check_day_c,
                spec_paths["300er"] / f"{str(year)[-2:]}-av300_{year}" / check_day,
            ]
        )
    # Account for different structure in 2019/start of 2020
    if year <= 2020:
        check_path_list.extend(
            [
                spec_paths["400er"] / f"{str(year)[-2:]}-av400_{year}" / check_day,
                spec_paths["300er"] / f"{str(year)[-2:]}-dpx300_{year}" / check_day,
            ]
        )
    return check_path_list


def get_hf_paths(spec_paths, check_year, wild_group):
    # At the moment there is just one folder per group
    # Check folders of all groups when group `nmr` uses the group wildcard
    if wild_group is True:
        group_folders = [
            x for x in spec_paths["hf"].parent.iterdir()
            if x.is_dir() and (x.name[0] != ".")
        ]
        check_path_list = [group_folder / check_year for group_folder in group_folders]
    else:
        check_path_list = [spec_paths["hf"] / check_year]
    return check_path_list


def get_check_paths(spec_paths, spectrometer, check_date, wild_group):
    """Get list of folders that may contain spectra, appropriate for the spectrometer."""

    if spectrometer == "300er" or spectrometer == "400er":
        if spectrometer == "300er":
            check_path_list = get_300er_paths(spec_paths, check_day=check_date)
        elif spectrometer == "400er":
            check_path_list = get_400er_paths(spec_paths, check_day=check_date)
        # Add potential overflow folders for same day (these are generated on mora when two samples
        # are submitted with same exp. no.)
        for entry in list(check_path_list):
            for num in range(2, 20):
                check_path_list.append(entry.with_name(entry.name + "_" + str(num)))

    elif spectrometer == "hf":
        check_path_list = get_hf_paths(
            spec_paths,
            check_year=check_date,
            wild_group=wild_group,
        )

    # Go over the list to make sure we only bother checking paths that exist
    check_path_list = [path for path in check_path_list if path.exists()]
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


def get_metadata_bruker(folder: Path, mora_path) -> dict:
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
        "server_location": str(folder.relative_to(mora_path)),
        "group": group,
        "initials": initials,
        "sample_info": sample_info,  # All remaining parts of title
        "experiment": details[0],
        "solvent": details[1],
        "frequency": None,
    }
    return metadata


def get_metadata_agilent(folder: Path, mora_path) -> dict:
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
        "server_location": str(folder.relative_to(mora_path)),
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
    return name


def format_name_klaus(folder, metadata) -> str:
    """Format folder name in Klaus' desired fashion."""
    # First do normally but with everything included
    name = format_name(folder, metadata, inc_group=True, inc_init=True, inc_solv=True)
    # Add location details in front
    name = metadata["server_location"].replace("/", "_").replace("\\", "_") + "_" + name
    return name


def compare_spectra(mora_folder, dest_folder) -> int:
    """Check that two spectra with the same name are actually identical and not e.g. different proton measurements.

    In the event that the spectra are the same, a check is made to see if everything has
    been copied; if not, `incomplete` is returned as `True`.
    Result is a tuple with the result in the form `(identical, incomplete)`.
    """

    comparison = filecmp.dircmp(mora_folder, dest_folder)
    if len(comparison.right_only) > 0:
        identical, incomplete = False, False
    elif len(comparison.left_only) == 0:
        identical, incomplete = True, False
    elif len(comparison.left_only) > 0:
        identical, incomplete = True, True

    return identical, incomplete


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
    identical_spectrum_found = False
    incomplete_copy = False
    if target.exists() is True:
        logging.info("Spectrum with this name exists in destination")
        # Check that the spectra are actually identical and not e.g. different
        # proton measurements
        # If confirmed to be unique spectra, need to extend spectrum name with
        # -2, -3 etc. to avoid conflict with spectra already in dest
        identical_spectrum_found, incomplete_copy = compare_spectra(src, target)
        num = 1
        while target.exists() is True and identical_spectrum_found is False:
            num += 1
            target = target.with_name(target.name + "-" + str(num))
            identical_spectrum_found, incomplete_copy = compare_spectra(src, target)

    # Try and fix only partially copied spectra
    if identical_spectrum_found is True and incomplete_copy is True:
        logging.info("The existing copy is only partial")
        for subfolder in src.iterdir():
            if not (target / subfolder.name).exists():
                try:
                    shutil.copytree(subfolder, target / subfolder.name)
                except PermissionError:
                    output.append(
                        "you do not have permission to write to the given folder"
                    )
                    return output
        text_to_add = "new files found for: " + target.name
        output.append(text_to_add)

    elif identical_spectrum_found is False:
        try:
            shutil.copytree(src, target)
        except PermissionError:
            output.append("you do not have permission to write to the given folder")
            logging.info("No write permission for destination")
            return output
        text_to_add = "spectrum found: " + target.name
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


def check_nmr(
    fed_options,
    mora_path,
    spec_paths,
    check_date,
    wild_group,
    prog_bar,
    progress_callback=None,
    status_callback=None,
):
    """Main checking function for Mora the Explorer."""

    # Some initial setup that is the same for all spectrometers
    logging.info(f"Beginning check of {check_date} with the options:")
    logging.info(fed_options)
    # Initialize list that will be returned as output
    output_list = ["no new spectra"]
    # Confirm destination directory exists
    if Path(fed_options["dest_path"]).exists() is False:
        logging.info("Given destination folder not found!")
        output_list.append("given destination folder not found!")
        return output_list
    # Confirm mora can be reached
    if mora_path.exists() is False:
        logging.info("The mora server could not be reached!")
        output_list.append("the mora server could not be reached!")
        return output_list
    spectrometer = fed_options["spec"]

    # Directory discovery
    check_path_list = get_check_paths(spec_paths, spectrometer, check_date, wild_group)

    # Give message if no directories for the given date exist yet
    if len(check_path_list) == 0:
        logging.info("No folders exist for this date!")
        output_list.append("no folders exist for this date!")
        return output_list
    else:
        logging.info("The following paths will be checked for spectra:")
        logging.info(check_path_list)

    # Initialize progress bar
    prog_state = 0
    n_spectra = get_number_spectra(paths=check_path_list)
    logging.info(f"Total spectra in these paths: {n_spectra}")
    try:
        prog_bar.setMaximum(n_spectra)
        if progress_callback is not None:
            progress_callback.emit(0)  # Reset bar to 0
        else:
            print(f"Total spectra to check: {n_spectra}")
    except Exception:
        # This stops Python from hanging when the program is closed, no idea why
        sys.exit()

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
                if spectrometer == "300er" or spectrometer == "400er":
                    metadata = get_metadata_bruker(folder, mora_path)
                # Save a step by not extracting metadata unless initials in folder name
                # as folders are given the name of the sample on 500 and 600 MHz specs
                elif fed_options["initials"] in folder.name:
                    hit = True
                    metadata = get_metadata_agilent(folder, mora_path)
                else:
                    prog_state = iterate_progress(prog_state, 1, progress_callback)
                    continue
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
                new_folder_name = format_name_klaus(
                    folder,
                    metadata,
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
            prog_bar.setMaximum(prog_bar.maximum() + 5)
            prog_state = iterate_progress(prog_state, 5, progress_callback)

    now = datetime.now().strftime("%H:%M:%S")
    completed_statement = f"check of {check_date} completed at " + now
    output_list.append(completed_statement)
    logging.info(completed_statement)
    return output_list
