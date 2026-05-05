"""UI-independent backend logic for checking the server and copying new spectra."""

from abc import ABC, abstractmethod
from enum import IntEnum
import filecmp
import logging
from os import PathLike
import re
import shutil
import datetime
from pathlib import Path

from .metadata import (
    MeasurementMetadata,
    MetadataRules,
    Manufacturer,
    get_metadata,
)


class SpectraSorting(IntEnum):
    """The way in which spectra should be sorted when copied to the destination.
    
    Sorting by measurement means all measurement folders are copied individually
    and stored in the same folder. This is effectively no extra sorting, and is
    the Bruker style.

    Sorting by sample means all measurements on the same sample are grouped
    together into a single folder, with the measurements as subfolders. This is
    the Agilent style.

    Sorting by sample and spectrometer means that all measurements on the same
    sample are grouped, but only if they were measured on the same spectrometer.
    This way, spectra measured on Bruker and Agilent spectrometers can be kept
    separate.

    Original sorting means that Bruker spectra are sorted by measurement and
    Agilent spectra by sample.
    """
    ORIGINAL = 0
    MEASUREMENT = 1
    SAMPLE_AND_SPEC = 2
    SAMPLE = 3


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


def cmp_spectra(src: Path, target: Path, src_metadata: MeasurementMetadata) -> tuple[bool, bool]:
    """Check that two spectra with the same name are actually the same measurement
    and not e.g. different proton measurements.

    In the event that the spectra are the same, a check is made to see if everything has
    been copied; if not, `incomplete` is returned as `True`.
    Result is a tuple with the result in the form `(same, incomplete)`.
    """

    # Compare metadata
    # We should distinguish between the situations where:
    # 1. the metadata actually differ in some field
    # 2. the previously copied metadata are less complete than the other, but all
    #    overlapping fields are identical
    # as the second case could pertain to two copies of the same spectrum if the
    # first time it was copied it didn't have all the necessary files available
    # to extract the metadata from, or the extraction rules were different, or
    # it was copied with an older version of the app where fewer fields were
    # extracted.

    # We know the src metadata already
    # Load that of the target from the TOML file we left behind when we copied it
    target_metadata_file = target / "mora.toml"
    metadata_match = True  # Assume a match until anything proves it wrong
    metadata_incomplete = False
    if not target_metadata_file.exists():
        metadata_match = False
        metadata_incomplete = False
    else:
        try:
            target_metadata: MeasurementMetadata = MeasurementMetadata.from_toml(target_metadata_file)
        except TypeError:
            # Probably caused by the metadata being old and containing a field that is no longer valid
            try:
                target_metadata: MeasurementMetadata = MeasurementMetadata.from_toml(
                    target_metadata_file,
                    ignore_invalid=True,
                )
                # If that isn't the case, an exception will be raised again, otherwise
                # we consider the metadata to be outdated and therefore incomplete
                metadata_incomplete = True
            except Exception:
                metadata_match = False
                metadata_incomplete = False
        except Exception:
            metadata_match = False
            metadata_incomplete = False
        # Check if the src is a superset of target (unless we already know it's not)
        if metadata_match:
            for f in target_metadata.fields(skip_missing=True):
                target_val = getattr(target_metadata, f)
                src_val = getattr(src_metadata, f)
                if target_val == src_val:
                    continue
                else:
                    logging.info(f"Metadata field {f} differs: {src_val} in src, {target_val} in target")
                    metadata_match = False
        # If it's a superset, check if they're actually truly identical or if there's stuff missing
        # (unless we already know there is)
        if metadata_match and not metadata_incomplete:
            metadata_incomplete = not (src_metadata == target_metadata)
    if metadata_match:
        logging.info("Metadata match (are not contradictory)")
        if metadata_incomplete:
            logging.info("Metadata in target appear to be incomplete")
    else:
        logging.info("Metadata do not match, implying different spectra")

    # Compare fids
    # fid is a binary file at the top level in a measurement folder regardless of manufacturer
    src_fid = src / "fid"
    target_fid = src / "fid"
    fids_match = filecmp.cmp(src_fid, target_fid)

    # Err on the side of caution - can only be sure they're the same if both matched
    same = fids_match and metadata_match
    # If the metadata and fids match, but there are missing metadata, it should be recopied
    incomplete = same and metadata_incomplete

    return same, incomplete


def copy_folder(src: Path, target: Path, src_metadata: MeasurementMetadata, reporter: Reporter) -> Path | None:
    """Copy a spectra folder over to the target if it isn't already there.

    Returns the destination that was saved to, if any.

    Also adds a `mora_meta` file (in TOML format) containing the metadata that was extracted.

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
        same_spectrum_found, incomplete_copy = cmp_spectra(src, target, src_metadata)
        num = 1
        while not same_spectrum_found:
            num += 1
            alt = target.with_name(target.name + "-" + str(num))
            if alt.exists():
                # Check if this spectrum is the same one or yet another unique one
                same_spectrum_found, incomplete_copy = cmp_spectra(src, alt, src_metadata)
            else:
                # We have exhausted all possible candidates for the same spectrum,
                # it's definitely not already been copied, and we have now finally
                # arrived at a new unique name, so stop the loop and use it
                target = alt
                break

    # Don't copy spectra yet if they have no fid or only a small placeholder fid
    fid = src / "fid"
    if not fid.exists():
        logging.info(f"No fid found for {src.name}!")
        reporter.add_error(f"No fid found for {src.name}!")
    
    # Even a proton spectrum is 200-250 KiB, so assume anything smaller than one
    # kilobyte is malformed
    if fid.stat().st_size < 1028:
        logging.info(f"fid of {src.name} is less than a KiB and presumed malformed")
        reporter.add_error(f"fid of {src.name} is invalid!")
        return None

    # Try and fix only partially copied spectra by copying them again
    if same_spectrum_found and incomplete_copy:
        logging.info("The existing copy is only partial")
        reporter.set_status("Copying…")
        reporter.add_message("New files found for: " + target.name)
        # Used to try and just add the missing files, but easier just to replace
        # entirely (as long as we are sure that they are the same spectra)
        try:
            shutil.copytree(src, target)
        except PermissionError:
            logging.info("No write permission for destination")
            reporter.add_error("You do not have permission to write to the given folder")
            return None
        logging.info(f"Spectrum overwritten with fresh copy at {target}")
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
        logging.info(f"Spectrum saved to {target}")
        reporter.add_copied(target.name)
        return target
    else:
        # Identified an existing copy of the spectrum
        logging.info(f"Copy of the spectrum already found at {target}")
        return None


def filter_and_expand_sample_dirs(
    check_paths: list[Path],
    rules: MetadataRules,
    manufacturer: Manufacturer,
) -> list[Path]:
    """Expand a list of directories containing sample directories into a list
    of measurement directories that match the provided rules.
    
    The Bruker spectrometers don't group spectra by sample, so this just returns
    all the measurement directories in all `check_paths`.

    On Agilent spectrometers, it returns a list of all the `.fid` subdirectories
    across all of the sample directories across all `check_paths`, but only after
    filtering them to restrict them to those that match `rules.sample_pattern`.
    (This generally means that the sample directory name starts with the value of
    `user`.)
    """
    measurement_dirs = []
    # We handle Bruker and Agilent a bit differently
    # Each folder in check_paths contains subfolders either for individual measurements (Bruker)
    # or for different samples with multiple measurements in each folder (Agilent)
    # For Agilent checks we thus expand each entry in check_paths, but since the
    # user's initials should appear in the title of the sample folder, and each
    # measurement folder ends with `.fid`, we can do some preliminary filtering
    # to save checking every single one of them
    if manufacturer is Manufacturer.AGILENT:
        # Get the expected pattern for the sample folder title
        pattern: re.Pattern = rules.sample_pattern
        for check_path in check_paths:
            sample_folders = [
                x for x in check_path.iterdir()
                if x.is_dir()
                and pattern.fullmatch(x.name)
            ]
            for sample_folder in sample_folders:
                measurement_dirs.extend([
                    x for x in sample_folder.iterdir()
                    if x.is_dir()
                    #and x.suffix == ".fid"  # Not needed since we'll be checking for exact regex matches!
                ])
    else:
        for check_path in check_paths:
            measurement_dirs.extend([
                x for x in check_path.iterdir()
                if x.is_dir()
                #and not x.name.startswith(".")  # Ignore hidden directories - but not needed since we'll be checking for exact regex matches!
            ])
    return measurement_dirs


def confirm_check_paths(check_paths: list[PathLike]) -> list[Path]:
    """Confirm the server can be reached and filter the paths to those at which
    directories actually exist.
    
    Converts all `PathLike`s to `Path` objects.

    For directories that do exist, the existence of additional overflow directories
    is also checked for, and any found are added to the list.
    """
    valid_paths: list[Path] = []
    not_found = []
    for p in check_paths:
        p = Path(p)
        if p.exists() is False:
            not_found.append(f"No folder could be found at {p}")
        else:
            valid_paths.append(p)
            # Look for potential overflow folders for same day (these are generated
            # on mora when two samples are submitted with same exp. no.)
            for n in range(2, 99):
                overflow_path = p.with_name(p.name + f"_{n}")
                if overflow_path.exists():
                    valid_paths.append(overflow_path)
                else:
                    # Stop as soon as we reach the max number
                    break
    if len(valid_paths) == 0:
        logging.info("No folders could be found!")
        for message in not_found:
            logging.info(message)
    else:
        logging.info("The following paths could be reached and will be checked for new spectra:")
        for p in valid_paths:
            logging.info(str(p))
    
    return valid_paths


def check_nmr(
    src: list[PathLike],
    dest: PathLike,
    rules: MetadataRules,
    manufacturer: Manufacturer,
    reporter: Reporter,
    date: datetime.date | None = None,
    sort: SpectraSorting = SpectraSorting.SAMPLE_AND_SPEC,
):
    """Main checking function for Mora the Explorer."""

    reporter.set_status("Preparing…")

    logging.info("Checking with the following options:")
    logging.info(f"- Match conditions: {rules.substitutions}")
    logging.info(f"- Save location: {dest}")

    # Some initial setup that is the same for all spectrometers
    # Confirm destination directory exists
    dest_path = Path(dest)
    if dest_path.exists() is False:
        logging.info("Given destination folder not found!")
        reporter.add_error("Given destination folder not found!")
    # Confirm source directories exist
    check_paths = confirm_check_paths(src)
    if not check_paths:
        reporter.add_error("No folders could be found!")

    reporter.reset_progress()

    measurement_dirs = filter_and_expand_sample_dirs(check_paths, rules, manufacturer)

    # Initialize progress bar
    n_measurements = len(measurement_dirs)
    # If we are checking an Agilent spectrometer, let's assume that the above
    # filtering and expansion operation took some time, and now that it's done
    # make the progress bar move by an appropriate amount
    if manufacturer is Manufacturer.AGILENT:
        logging.info(f"Total spectra in these paths matching the given user: {n_measurements}")
        reporter.set_max_progress(n_measurements + 10)
        reporter.increment_progress(10)
    else:
        logging.info(f"Total spectra in these paths: {n_measurements}")
        reporter.set_max_progress(n_measurements)
    reporter.set_status("Checking…")

    # Start the actual search process
    # Needs to be slightly different depending on the spectrometer, as the contents of
    # the folder for a spectrum is manufacturer-dependent

    logging.info("The following spectra were checked for potential matches:")
    # Loop over all the measurements
    for measurement_dir in measurement_dirs:
            logging.info(measurement_dir)

            # Resolve the metadata fully
            try:
                metadata = get_metadata(measurement_dir, rules, manufacturer)
            except FileNotFoundError:
                reporter.add_error(f"No metadata could be found for {measurement_dir}!")
                logging.info("No metadata found")
                reporter.increment_progress()
                continue

            # Might have failed to match, in which case we move on to the next spectrum
            if not metadata:
                # Update progress bar
                reporter.increment_progress()
                continue
            else:
                logging.info("Spectrum matches search query!")
            
            logging.debug(f"Measurement title: {metadata.title}")

            # Some things are not typically resolved by the get_metadata function
            # (at least not at this point in time)
            # but can be supplied because we know them already
            metadata.manufacturer = manufacturer
            if metadata.submission_time is None:
                metadata.submission_time = datetime.datetime(date.year, date.month, date.day)

            # Generate the appropriate names and target path
            measurement_name = metadata.generate_folder_name(rules, drop_missing=False)
            if sort is SpectraSorting.ORIGINAL:
                # Use the native Bruker or Agilent style
                sort = SpectraSorting.MEASUREMENT if manufacturer is Manufacturer.BRUKER else SpectraSorting.SAMPLE
            if sort is SpectraSorting.MEASUREMENT:
                # Just save spectra in a completely flat fashion
                target = dest_path / measurement_name
            else:  # Covers sorting by sample and by sample+spectrometer
                sample_name = metadata.generate_folder_name(rules, drop_missing=False, sample=True)
                # Save in nested folders
                target = dest_path / sample_name / measurement_name

            # Copy, add output messages to main output list
            reporter.set_status("Comparing metadata…")
            final_dest = copy_folder(measurement_dir, target, metadata, reporter)

            # If we copied, add a file with the metadata
            if final_dest:
                metadata.write_toml(final_dest / "mora.toml")

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
