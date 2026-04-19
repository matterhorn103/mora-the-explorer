"""UI-independent backend logic for checking the server and copying new spectra."""

from abc import ABC, abstractmethod
import filecmp
import logging
from os import PathLike
import shutil
import sys
import datetime
from pathlib import Path

from .metadata import (
    MetadataRules,
    Manufacturer,
    generate_folder_name,
    get_metadata,
)


class Reporter(ABC):

    @abstractmethod
    def set_status(self, message: str):
        """Set the current status of the check."""
        pass

    @abstractmethod
    def progress(self) -> int:
        """Get the current extent of progress as an absolute value."""
        pass

    @abstractmethod
    def reset_progress(self):
        """Set the current progress to zero."""
        pass

    @abstractmethod
    def increment_progress(self, increment: int = 1):
        """Increase the current progress by `increment`."""
        pass

    @abstractmethod
    def max_progress(self) -> int:
        """Get the absolute value of the progress that represents completion, currently."""
        pass

    @abstractmethod
    def set_max_progress(self, max: int):
        """Set the absolute value of the progress that represents completion."""
        pass

    @abstractmethod
    def messages(self) -> list[str]:
        """Get all general messages returned during the check."""

    @abstractmethod
    def add_message(self, message: str):
        """Add a general message that should be reported to the user by an appropriate mechanism."""
        pass

    @abstractmethod
    def copied(self) -> list[str]:
        """Get the names of all measurement folders copied during the check."""

    @abstractmethod
    def add_copied(self, name: str):
        """Add a measurement folder to the list of copied folders.
        
        The name is the name of the folder as saved in the destination location.
        """
        pass

    @abstractmethod
    def errors(self) -> list[str]:
        """Get all error messages returned during the check."""

    @abstractmethod
    def add_error(self, error: str):
        """Add an error message that should be reported to the user by an appropriate mechanism."""
        pass

    @abstractmethod
    def finish(self, completion_message: str):
        """Signal that the check has completed and pass a completion message to the user by an
        appropriate mechanism.
        
        It is expected that the completion message will also be added to the normal list of messages.
        """
        pass


def get_number_spectra(paths: list[Path]):
    """Get the total number of spectra folders in the given directories.

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


def compare_spectra(server_folder, dest_folder) -> tuple[bool, bool]:
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


def copy_folder(src: Path, target: Path, reporter: Reporter) -> Path | None:
    """Copy a spectra folder over to the target if it isn't already there.

    Returns the destination that was saved to, if any.

    Note that `target` should be the target path of the copied folder, not a directory
    to copy it into.

    Should the target already exist, it is assessed whether the folder at the target is
    indeed the same spectrum/spectra or if it just has the same name.

    If the latter is the case, it is copied with a number appended to the name.

    Partial copies are also checked for and recopied if they are incomplete.
    """
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
        reporter.set_status("Copying additional files…")
        reporter.add_message("New files found for: " + target.name)
        for x in src.iterdir():
            # Copy any file or subdirectory that isn't already in destination
            if not (target / x.name).exists():
                try:
                    if x.is_dir():
                        shutil.copytree(x, target / x.name)
                    elif x.is_file():
                        shutil.copy2(x, target / x.name)
                except PermissionError:
                    reporter.add_error("You do not have permission to write to the given folder")
                    return None
        reporter.add_copied(target.name)
        return target
    elif same_spectrum_found is False:
        reporter.set_status("Copying…")
        try:
            shutil.copytree(src, target)
        except PermissionError:
            logging.info("No write permission for destination")
            reporter.add_error("You do not have permission to write to the given folder")
            return None
        logging.info(f"Spectrum saved to {target.name}")
        reporter.add_copied(target.name)
        return target
    else:
        return None


def check_nmr(
    src: list[PathLike],
    dest: PathLike,
    rules: MetadataRules,
    manufacturer: Manufacturer,
    reporter: Reporter,
    date: datetime.date | None = None,
):
    """Main checking function for Mora the Explorer."""

    reporter.set_status("Preparing…")

    logging.info("Checking with the following options:")
    logging.info(f"- Match conditions: {rules.conditions}")
    logging.info(f"- Save location: {dest}")

    # Some initial setup that is the same for all spectrometers
    # Confirm destination directory exists
    dest_path = Path(dest)
    if dest_path.exists() is False:
        logging.info("Given destination folder not found!")
        reporter.add_error("Given destination folder not found!")
    # Confirm server can be reached
    check_paths = []
    not_found = []
    for p in src:
        p = Path(p)
        if p.exists() is False:
            not_found.append(f"No folder could be found at {p}")
        else:
            check_paths.append(p)
            # Look for potential overflow folders for same day (these are generated
            # on mora when two samples are submitted with same exp. no.)
            for n in range(2, 99):
                overflow_path = p.with_name(p.name + f"_{n}")
                if overflow_path.exists():
                    check_paths.append(overflow_path)
                else:
                    # Stop as soon as we reach the max number
                    break
    if len(check_paths) == 0:
        logging.info("No folders could be found!")
        for message in not_found:
            logging.info(message)
        reporter.add_error("No folders could be found!")
    else:
        logging.info("The following paths could be reached and will be checked for new spectra:")
        for p in check_paths:
            logging.info(str(p))

    # Initialize progress bar
    # Get total number of folders that we're going to be checking across all src paths
    n_spectra = get_number_spectra(paths=check_paths)
    logging.info(f"Total spectra in these paths: {n_spectra}")
    try:
        reporter.set_max_progress(n_spectra)
        reporter.reset_progress()
    except Exception:
        # This stops Python from hanging when the program is closed, no idea why
        sys.exit()
    reporter.set_status("Checking…")

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

            # Extract title and experiment details from title file in spectrum folder
            try:
                # For Agilent spectra the name of the folder itself ought to include the user
                # initials so if that's a condition for a match (it usually is) we can save
                # some time by checking for it straight away and short-circuiting if they are
                # are missing from the folder name of the sample
                if (
                    manufacturer is Manufacturer.AGILENT
                    and "user" in rules.conditions
                    and rules.conditions["user"] not in folder.name
                ):
                    logging.info("User missing from folder name - skipping detailed metadata analysis")
                    reporter.increment_progress()
                    continue
                # Otherwise resolve the metadata fully
                metadata = get_metadata(folder, rules, manufacturer)
                logging.info(f"Measurement title: {metadata.title}")
                # Some things are not typically resolved by the get_metadata function
                # but can be supplied because we know them already
                metadata.manufacturer = manufacturer
                if metadata.date is None:
                    metadata.date = date
            except FileNotFoundError:
                reporter.add_error(f"No metadata could be found for {folder}!")
                logging.info("No metadata found")
                reporter.increment_progress()
                continue
            except IndexError:  # Due to title not being long enough
                reporter.increment_progress()
                continue

            if not metadata.matches_rules(rules):
                # Update progress bar
                reporter.increment_progress()
                continue
            else:
                logging.info("Spectrum matches search query!")

            # Formatting
            new_folder_name = generate_folder_name(metadata, rules)

            # Copy, add output messages to main output list
            reporter.set_status("Comparing metadata…")
            _copy_dest = copy_folder(folder, dest_path / new_folder_name, reporter)

            # Update progress bar to make sure there's a noticeable movement after
            # copying a spectrum, otherwise it looks frozen
            reporter.set_max_progress(reporter.max_progress() + 5)
            reporter.increment_progress(5)
            
            # Go back to checking
            reporter.set_status("Checking…")

    now = datetime.datetime.now().strftime("%H:%M:%S")
    completed_statement = f"Check of {date} completed at {now}"
    logging.info(completed_statement)
    reporter.finish(completed_statement)
