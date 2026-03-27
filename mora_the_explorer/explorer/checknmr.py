"""All UI-independent backend logic for checking the server and copying new spectra."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import filecmp
import logging
from os import PathLike
import shutil
import sys
from datetime import datetime
from pathlib import Path


class Manufacturer(Enum):
    BRUKER = 1
    AGILENT = 2

    @classmethod
    def from_str(s: str):
        if s.lower() == "bruker":
            Manufacturer.BRUKER
        elif s.lower() == "agilent":
            Manufacturer.AGILENT
        else:
            raise ValueError("Only Bruker and Agilent are recognized manufacturers!")


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


@dataclass
class MeasurementMetadata():
    server_location: str
    group: str | None
    initials: str
    experiment: str | None
    solvent: str | None
    frequency: str | None
    other_sample_info: list[str]


def get_metadata_bruker(folder: Path, server_path: Path) -> MeasurementMetadata:
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
            # Still keep rest of second item in title as first part of sample info
            # If spectra submitted in form "stu msc-jo 004", don't keep the hyphen, so
            # for this example should get `initials="msc"`, `sample_info=["jo", "004"]`
            sample_info = (
                [title[1][3:]] if title[1][3].isalnum() else [title[1][4:]]
                + title[2:]
            )
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

    metadata = MeasurementMetadata(
        server_location=str(folder.relative_to(server_path)),
        group=group,
        initials=initials,
        other_sample_info=sample_info,  # All remaining parts of title
        experiment=details[0],
        solvent=details[1],
        frequency=None,
    )
    return metadata


def get_metadata_agilent(folder: Path, server_path: Path) -> MeasurementMetadata:
    # Find out magnet strength, set to None initially
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

    metadata = MeasurementMetadata(
        server_location=str(folder.relative_to(server_path)),
        group=None,
        initials=folder.name[:3],
        other_sample_info=[folder.name[3:]],  # A list so as to match the Bruker version
        experiment=None,
        solvent=None,
        frequency=magnet_freq,
    )
    return metadata


def format_name(
    folder: Path,
    metadata: MeasurementMetadata,
    inc_group: bool = False,
    inc_init: bool = False,
    inc_solv: bool = False,
    nmrcheck_style: bool = False,
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
                    metadata.initials,
                    *(metadata.other_sample_info),
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
                    *(metadata.other_sample_info),
                    metadata.experiment,
                ]
                if x is not None
            ]
        )
    # Apply user choices, some only if NMRCheck style wasn't chosen
    if nmrcheck_style is False:
        if inc_init is True and metadata.initials is not None:
            name = metadata.initials + "-" + name
        if inc_group is True and metadata.group is not None:
            name = metadata.group + "-" + name
    if inc_solv is True and metadata.solvent is not None:
        name = name + "-" + metadata.solvent
    # Add frequency info if available
    if metadata.frequency is not None:
        name = name + "_" + metadata.frequency
    # Make sure there are no special characters in the name, and if so, replace them
    # with the Unicode hexadecimal code points
    # Otherwise Windows will likely reject them
    # Replacing rather than just removing ensures the name is still unique compared to
    # other spectra
    # alphanumeric characters, space, hyphen, underscore are allowed
    allowed_symbols = ["-", "_", " "]
    special = set([x for x in name if not x.isalnum() and x not in allowed_symbols])
    for x in special:
        logging.info(
            f"Char {x} not permitted in spectrum names, replaced with {str(hex(ord(x)))}"
        )
        name = name.replace(x, str(hex(ord(x))))
    return name


def format_name_admin(
    folder,
    metadata: MeasurementMetadata,
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
        location = metadata.server_location.replace("/", "_").replace("\\", "_")
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
        server_folder,
        dest_folder,
        diagnostic_files,
        shallow=False,
    )
    if len(top_level_cmp[0]) > 0:
        same = True
        logging.info(
            f"Determined to be the same based on {top_level_cmp[0]} being identical"
        )

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


cache = tuple()
cached_paths = []


def check_nmr(
    reporter: Reporter,
    server_path: PathLike,
    check_paths: list[str],
    dest_path: PathLike,
    manufacturer: Manufacturer,
    initials: str,
    group: str,
    inc_init: bool = False,
    inc_solv: bool = False,
    inc_path: bool = False,
    nmrcheck_compat_mode: bool = False,
):
    """Main checking function for Mora the Explorer."""

    reporter.set_status("preparing...")

    logging.info("Beginning check with the options:")
    logging.info(f"{server_path = }")
    logging.info(f"{check_paths = }")
    logging.info(f"{dest_path = }")
    logging.info(f"{manufacturer = }")
    logging.info(f"{initials = }")
    logging.info(f"{inc_init = }")
    logging.info(f"{inc_solv = }")
    logging.info(f"{inc_path = }")
    logging.info(f"{nmrcheck_compat_mode = }")

    # Some initial setup that is the same for all spectrometers
    # Initialize list that will be returned as output
    output_list = ["No new spectra"]
    # Confirm destination directory exists
    dest_path = Path(dest_path)
    if dest_path.exists() is False:
        logging.info("Given destination folder not found!")
        output_list.append("Given destination folder not found!")
        return output_list
    # Confirm server can be reached
    server_path = Path(server_path)
    if server_path.exists() is False:
        logging.info("The NMR server could not be reached!")
        output_list.append("The NMR server could not be reached!")
        return output_list

    check_path_list = [server_path / p for p in check_paths]
    logging.info("The following paths will be checked for spectra:")
    logging.info(check_path_list)

    # Initialize progress bar
    n_spectra = get_number_spectra(paths=check_path_list)
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
    # Loop through each folder in check_path_list
    for check_path in check_path_list:
        # Iterate through spectra
        for folder in check_path.iterdir():
            logging.info(folder)

            hit = False

            # Extract title and experiment details from title file in spectrum folder
            try:
                if manufacturer is Manufacturer.BRUKER:
                    metadata = get_metadata_bruker(folder, server_path)
                elif manufacturer is Manufacturer.AGILENT:
                    # Save a step by not extracting metadata unless initials in folder
                    # name as folders are given the name of the sample on Agilent specs
                    if initials in folder.name:
                        hit = True
                        metadata = get_metadata_agilent(folder, server_path)
                    else:
                        reporter.increment_progress()
                        continue
            except FileNotFoundError:
                output_list.append(f"No metadata could be found for {folder}!")
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
            elif (
                group == "nmr"
                and metadata.group == initials
            ):
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
            output_list.extend(
                copy_folder(folder, dest_path/new_folder_name)
            )
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
