"""UI-independent backend logic for checking the server and copying new spectra."""

from abc import ABC, abstractmethod
import filecmp
import logging
from os import PathLike
import shutil
import sys
from datetime import datetime
from pathlib import Path

from .metadata import (
    MeasurementMetadata,
    MetadataRules,
    Manufacturer,
    generate_folder_name,
    get_metadata,
)


class Reporter(ABC):
    @abstractmethod
    def set_status(self, message: str):
        pass

    @abstractmethod
    def progress(self) -> int:
        pass

    @abstractmethod
    def reset_progress(self):
        pass

    @abstractmethod
    def increment_progress(self, increment: int = 1):
        pass

    @abstractmethod
    def max_progress(self) -> int:
        pass

    @abstractmethod
    def set_max_progress(self, max: int):
        pass

    @abstractmethod
    def append_output(self, line: str):
        pass


def get_number_spectra(paths: list[Path]):
    """Get the total number of spectra folders in the given directory or directories.

    We can then use the length of it to measure progress.
    """
    # Can't remember why it was done this way, I guess the hf check used to be done
    # differently to how it is today
    #if paths is None:
    #    n = sum(1 for x in path.iterdir() if x.is_dir())
    #else:
    #    n = 0
    #    for path in paths:
    #        n += sum(1 for x in path.iterdir() if x.is_dir())
    n = 0
    for path in paths:
        n += sum(1 for x in path.iterdir() if x.is_dir())
    return n


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
        server_folder,
        dest_folder,
        diagnostic_files,
        shallow=False,
    )
    if len(top_level_cmp[0]) > 0:
        same = True
        logging.info(f"Determined to be the same based on {top_level_cmp[0]} being identical")

    # If don't seem to be same so far, check any subfolders (which are each spectra
    # on Agilent specs) to see if they are identical spectra
    if not same:
        for x in [x for x in server_folder.iterdir() if x.is_dir()]:
            subdir_cmp = filecmp.cmpfiles(
                x,
                dest_folder / x.name,
                diagnostic_files,
                shallow=False,
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
                    output.append("You do not have permission to write to the given folder")
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


def check_nmr(
    src: list[PathLike],
    dest: PathLike,
    manufacturer: Manufacturer,
    rules: MetadataRules,
    reporter: Reporter,
):
    """Main checking function for Mora the Explorer."""

    reporter.set_status("preparing...")

    logging.info("Checking the following paths for new spectra:")
    for p in src:
        logging.info(str(p))
    logging.info("Checking with the following options:")
    logging.info(f"- Match conditions: {rules.conditions}")
    logging.info(f"- Save location: {dest}")

    # Some initial setup that is the same for all spectrometers
    # Confirm destination directory exists
    dest_path = Path(dest)
    if dest_path.exists() is False:
        logging.info("Given destination folder not found!")
        reporter.append_output("Given destination folder not found!")
    # Confirm server can be reached
    check_paths = []
    for p in src:
        p = Path(p)
        if p.exists() is False:
            logging.info(f"No folder could be found at {p}")
            reporter.append_output(f"No folder could be found at {p}")
        else:
            check_paths.append(p)

    # Initialize progress bar
    n_spectra = get_number_spectra(paths=check_paths)
    logging.info(f"Total spectra in these paths: {n_spectra}")
    try:
        reporter.set_max_progress(n_spectra)
        reporter.reset_progress()
    except Exception:
        # This stops Python from hanging when the program is closed, no idea why
        sys.exit()
    reporter.set_status("checking...")

    # Start the actual search process
    # Needs to be slightly different depending on the spectrometer, as the contents of
    # the folder for a spectrum is manufacturer-dependent

    logging.info("The following spectra were checked for potential matches:")
    # Loop through each folder in check_paths
    # Each is a folder that contains measurement folders
    for check_path in check_paths:
        # Iterate over the measurement folders
        for folder in check_path.iterdir():
            logging.info(folder)

            hit = False

            # Extract title and experiment details from title file in spectrum folder
            try:
                if (
                    manufacturer is Manufacturer.AGILENT
                    and "user" in rules.conditions
                    and rules.conditions["user"] not in folder.name
                ):
                    # Save a step by short-circuiting if either the initials or full name of the
                    # user are missing from the folder name of the sample
                    reporter.increment_progress()
                    continue
                metadata = get_metadata(folder, rules, manufacturer)
            except FileNotFoundError:
                reporter.append_output(f"No metadata could be found for {folder}!")
                logging.info("No metadata found")
                reporter.increment_progress()
                continue
            except IndexError:  # Due to title not being long enough
                reporter.increment_progress()
                continue

            # Look for search string
            if metadata.initials == initials:
                hit = True
            # Klaus can give a group initialism as the initials and download all spectra
            # from a group
            elif group == "nmr" and metadata.group == initials:
                hit = True

            if not hit:
                # Update progress bar
                reporter.increment_progress()
                continue
            else:
                logging.info("Spectrum matches search query!")

            # Formatting
            if group == "nmr":
                new_folder_name = format_name_admin(
                    folder,
                    metadata,
                    inc_solv=inc_solv,
                    inc_path=inc_path,
                )
            else:
                new_folder_name = format_name(
                    folder,
                    metadata,
                    inc_init=inc_init,
                    inc_solv=inc_solv,
                    nmrcheck_style=nmrcheck_compat_mode,
                )

            # Copy, add output messages to main output list
            reporter.set_status("copying...")
            output_list.extend(copy_folder(folder, dest_path / new_folder_name))
            reporter.set_status("checking...")

            # Update progress bar if a callback object has been given
            # Make sure there's a noticeable movement after copying a spectrum,
            # otherwise it looks frozen
            if reporter is not None:
                reporter.set_max_progress(reporter.max_progress() + 5)
                reporter.increment_progress(5)

    now = datetime.now().strftime("%H:%M:%S")
    completed_statement = f"Check completed at {now}"
    output_list.append(completed_statement)
    logging.info(completed_statement)
    return output_list
