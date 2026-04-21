"""Metadata handling."""

from dataclasses import dataclass
import datetime
import logging
from pathlib import Path
import re
from typing import Self

from ..spec import Manufacturer


class MetadataRules:
    """Specifies rules for extracting and proliferating measurement metadata, as
    well as the required values for a match."""

    def __init__(
        self,
        src_fields: list[str],
        conditions: dict[str, str],
        dest_fields: list[str],
        src_sep: str = r"[\s\-_]+",
        dest_sep: str = "-",
    ):
        """Create a new rules specification.

        `src_fields` indicates the expected components of the measurement title.
        For Bruker spectra this is recorded in `./pdata/1/title`, while for
        Agilent spectra it forms the name of the measurement folder.
        (Note that this is not the only source of a measurement's metadata.)

        Title components are obtained from the title by separating on `src_sep`,
        which is a regex pattern.
        By default whitespace, hyphens, and underscores are treated as separators.
        The list of strings is considered as a list of variable names.
        The variable names used should be the same as the field names of
        `MeasurementMetadata`.
        All trailing components of the separated title are collected as the
        `sample_info` variable.

        For example, if `src_fields` is `["group", "user"]` then the measurement
        title `"stu mjm 213-4 repeat"` will be parsed to give
        `{"group": "stu", "user": "mjm", "sample_info": ["213", "4", "repeat"]}`

        If the maximum length of a field is known, or the field is not separated
        from the succeeding field by a separator character, the length of the
        field can be specified with the syntax `"variable:len"` e.g. `"user:3"`.
        Should the field exceed the specified length, the excess characters will
        be split off and placed at the next position.

        For example, if `src_fields` is `["user:3"]` then the
        measurement title `"mjm304-1"` will be parsed into
        `{"user": "mjm", "sample_info": ["304", "1"]}`

        `dest_fields` indicates the desired components to include in the
        measurement folder name when it is saved to the destination location.
        Again, the list of strings is considered as a list of variable names.
        strftime formatting strings beginning with `%` are replaced by the
        appropriately formatted component of the date.
        If an entry in the list is another sublist of strings, the first variable
        in the sublist with a value will be used i.e. they are treated as mutually
        exclusive.

        For example, if the above title had been supplemented by metadata from
        the spectrum files such that a few other variables were available:
        `{"frequency": "300", "solvent": "DMSO-d6"}`
        and `dest_fields` had the value `["user", "sample_info", "solvent"]`
        then the measurement folder would be saved with the path
        `<dest_path>/mjm-213-4-repeat-DMSO-d6/`

        Note that the only allowed characters in the save name are ASCII
        a-z, A-Z, 0-9, -, and _, and anything else is replaced by the Unicode
        code point (in hexadecimal).

        `conditions` specifies the conditions that are required to be met for
        a measurement to be considered a match for the search.
        Conditions are specified in a `dict` with variable names as the keys
        and the expected values as the values.
        If the expected value given is `None`, any value is considered a match.
        Matching is done case-insensitively.
        If a condition is given and the corresponding variable is not even
        present in the metadata, it is not considered a match.
        """

        self.src_fields = src_fields
        self.src_sep = src_sep
        # Normalize the expectation values to lowercase now, and drop any that
        # just have `None` as the value
        self.conditions = {k: v.casefold() for k, v in conditions.items() if v is not None}
        self.dest_fields = dest_fields
        self.dest_sep = dest_sep


@dataclass
class MeasurementMetadata:
    """The actual extracted metadata of a measurement."""

    path: str | None = None
    folder_name: str | None = None
    manufacturer: Manufacturer | None = None
    date: datetime.date | None = None
    title: str | None = None
    user: str | None = None
    user_name: str | None = None
    group: str | None = None
    group_name: str | None = None
    experiment: str | None = None
    frequency: int | None = None
    solvent: str | None = None
    sample_info: list[str] | None = None
    # Access fields programmatically using `getattr(mdata, field)` or `mdata.asdict()`

    @classmethod
    def from_title(cls, title: str, rules: MetadataRules) -> Self:
        # Split by every occurrence of one or more of -, _, or whitespace (or
        # whichever custom alternative was specified)
        components = re.split(rules.src_sep, title)
        variables = rules.src_fields

        # Make sure the variables and components will correspond cleanly
        for i, variable in enumerate(variables):
            if ":" in variable:
                split = variable.split(":")
                true_variable = split[0]
                length = int(split[1])
            else:
                true_variable = variable
                length = None
            # Slice the component to the appropriate length
            combined = components[i]
            if length and len(combined) > length:
                actual_component = combined[:length]
                following_component = combined[length:]
                components[i] = actual_component
                components.insert(i + 1, following_component)
            variables[i] = true_variable

        extracted = {}
        for i, component in enumerate(components):
            if i == len(variables):
                # No more variables specified, everything else is spare
                break
            extracted[variables[i]] = component

        # Any remaining components are collected together as `sample_info`
        if len(components) > len(rules.src_fields):
            extracted["sample_info"] = components[len(rules.src_fields) :]
        else:
            extracted["sample_info"] = []

        result = MeasurementMetadata(**extracted)

        # Add the original title too
        result.title = title

        return result

    def matches_rules(self, rules: MetadataRules) -> bool:
        """Check if the metadata match a set of rules.

        If the expected value given is `None`, any value is considered a match.
        Similarly, if a condition is given and the corresponding variable has no
        value (it is still set to `None`), the condition is treated as met.
        However, if a condition is given and the variable is not a metadata
        field, an `AttributeError` will be raised.

        Matching is done case-insensitively.
        """
        for variable, expectation in rules.conditions.items():
            if expectation is None:
                # Any value is a match
                continue
            actual = getattr(self, variable)
            if actual is None:
                # Ignore the condition
                continue
            if actual.casefold() != expectation:
                return False
        return True


def get_metadata_bruker(folder: Path, rules: MetadataRules) -> MeasurementMetadata:
    # Extract title and experiment details from title file in spectrum folder
    title_file = folder / "pdata/1/title"
    with open(title_file, encoding="utf-8") as f:
        title_contents = f.read().splitlines()
    if len(title_contents) < 2:
        logging.info("Title file is empty")
    title = title_contents[0]
    details = title_contents[1]
    metadata = MeasurementMetadata.from_title(title, rules)
    # Check that the title had enough components including sample info (no. etc.)
    if metadata.sample_info is None:
        logging.info("No sample name was given when submitting!")
        raise IndexError

    metadata.path = str(folder)
    metadata.folder_name = folder.name
    metadata.manufacturer = Manufacturer.BRUKER
    details_split = details.split()
    metadata.experiment = details_split[0]
    metadata.solvent = details_split[1]

    # Get magnet frequency
    uxnmr_info_file = folder / "uxnmr.info"
    if uxnmr_info_file.exists():
        with open(uxnmr_info_file, encoding="utf-8") as f:
            for line in f:
                if line.startswith("1H-frequency"):
                    # Line has format "1H-frequency : 300.26 MHz"
                    metadata.frequency = int(float(line.split()[2]))
                    break

    return metadata


def get_metadata_agilent(folder: Path, rules: MetadataRules) -> MeasurementMetadata:
    title = folder.name
    metadata = MeasurementMetadata.from_title(title, rules)
    metadata.path = str(folder)
    metadata.folder_name = folder.name
    metadata.manufacturer = Manufacturer.AGILENT
    # One folder contains multiple measurements
    metadata.experiment = "various"

    # Get magnet strength
    for subfolder in folder.iterdir():
        text_file = subfolder / "text"
        if text_file.exists():
            with open(text_file, encoding="utf-8") as f:
                spectrum_info = f.read().splitlines()
                # I assume that what we get here is the configured name of the spectrometer,
                # and it's just that the convention in Münster is to call them s600, v500 etc.,
                # so I don't know how portable this is
                try:
                    spec_name = spectrum_info[3].split(",")[0]
                except IndexError:
                    continue
                magnet_freq = ""
                for char in spec_name:
                    # Only want numbers, naturally
                    if char.isdigit():
                        magnet_freq += char
                if magnet_freq:
                    metadata.frequency = int(magnet_freq)
                    break

    # Get solvent
    # First try top-level `studypar` file
    studypar_file = folder / "studypar"
    if studypar_file.exists():
        with open(studypar_file, encoding="utf-8") as f:
            sample_info = f.read()
        # Contains two lines in the format
        # solvent 2 2 6 0 0 2 1 11 1 64
        # 1 "cdcl3"
        try:
            lines = sample_info.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("solvent"):
                    solvent = lines[i + 1].split()[1].strip('"')
                    metadata.solvent = solvent
        except Exception:
            pass
    # Failing that, try `sampleinfo`, buried a bit deeper
    sample_info_file = folder / "dirinfo/macdir/sampleinfo"
    if metadata.solvent is None and sample_info_file.exists():
        with open(sample_info_file, encoding="utf-8") as f:
            sample_info = f.read()
        # Contains a line in the format "SOLVENT: cdcl3"
        try:
            solvent = sample_info.splitlines()[3].split()[1]
            metadata.solvent = solvent
        except Exception:
            pass

    return metadata


def get_metadata(
    folder: Path, rules: MetadataRules, manufacturer: Manufacturer
) -> MeasurementMetadata:
    match manufacturer:
        case Manufacturer.BRUKER:
            return get_metadata_bruker(folder, rules)
        case Manufacturer.AGILENT:
            return get_metadata_agilent(folder, rules)
        case _:
            raise ValueError(f"{repr(manufacturer)} is not a valid manufacturer!")


def generate_folder_name(
    metadata: MeasurementMetadata,
    rules: MetadataRules,
    drop_missing: bool = True,
) -> str:
    """Format folder name according to the prescribed rules."""
    parts = []
    for field in rules.dest_fields:
        if isinstance(field, list):
            for mutually_exclusive_field in field:
                if getattr(metadata, mutually_exclusive_field, None) is not None:
                    field = mutually_exclusive_field
        if field.startswith("%"):
            # strftime formatting strings beginning with `%` are replaced by the
            # appropriately formatted component of the date
            parts.append(metadata.date.strftime(field))
        else:
            value = getattr(metadata, field, None)
            if isinstance(value, list):
                parts.extend(value)
                continue
            # What do we do if the user wants something in the folder name but
            # we don't have that information?
            if value is not None:
                parts.append(str(value))
            elif drop_missing:
                # Just don't include it at all
                continue
            else:
                # Use unknown in its place
                parts.append("unknown")
    # Join with desired separator, normalize to all lower case
    name = rules.dest_sep.join(parts).lower()
    # Normalize non-ASCII, non-alphanumerical characters
    allowed_symbols = ["-", "_", " "]
    special = set(
        [x for x in name if not x.isascii() or (not x.isalnum() and x not in allowed_symbols)]
    )
    for x in special:
        logging.info(f"Char {x} not permitted in folder names, replaced with {str(hex(ord(x)))}")
        name = name.replace(x, str(hex(ord(x))))
    return name
