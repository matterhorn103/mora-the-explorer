"""Metadata handling."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from pathlib import Path
import re
from typing import Self


class Manufacturer(Enum):
    BRUKER = 1
    AGILENT = 2

    @classmethod
    def from_str(cls, s: str):
        if s.lower() == "bruker":
            Manufacturer.BRUKER
        elif s.lower() == "agilent":
            Manufacturer.AGILENT
        else:
            raise ValueError("Only Bruker and Agilent are recognized manufacturers!")


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
    manufacturer: Manufacturer | None = None
    date: datetime | None = None
    user: str | None = None
    user_name: str | None = None
    group: str | None = None
    group_name: str | None = None
    experiment: str | None = None
    frequency: str | None = None
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

        return result
    

    def matches_rules(self, rules: MetadataRules) -> bool:
        """Check if the metadata match a set of rules.
        
        If the expected value given is `None`, any value is considered a match.
        Matching is done case-insensitively.
        If a condition is given and the corresponding variable is not even
        present in the metadata, it is not considered a match.
        """
        for variable, expectation in rules.conditions.values():
            if expectation is None:
                # Any value is a match
                continue
            actual = getattr(self, variable, "")
            if actual is None:
                # Can't be a match
                return False
            if actual.casefold() != expectation:
                return False
        return True


def get_metadata_bruker(folder: Path, rules: MetadataRules) -> MeasurementMetadata:
    # Extract title and experiment details from title file in spectrum folder
    title_file = folder / "pdata/1/title"
    with open(title_file, encoding="utf-8") as f:
        title_contents = f.readlines()
    if len(title_contents) < 2:
        logging.info("Title file is empty")
    title = title_contents[0]
    details = title_contents[1]

    # Old approach
    # title_split = title.split()
    # if len(title) >= 3:
    #    group = title[0]
    #    if len(title[1]) <= 3:
    #        initials = title[1]
    #        sample_info = title[2:]
    #    else:
    #        initials = title[1][:3]
    #        # Still keep rest of second item in title as first part of sample info
    #        # If spectra submitted in form "stu msc-jo 004", don't keep the hyphen, so
    #        # for this example should get `initials="msc"`, `sample_info=["jo", "004"]`
    #        sample_info = (
    #            [title[1][3:]] if title[1][3].isalnum() else [title[1][4:]]
    #            + title[2:]
    #        )
    # elif len(title) >= 2:
    #    # Presumably the initials were not separated correctly from the sample number
    #    group = title[0]
    #    initials = title[1][:3]
    #    try:
    #        sample_info = [title[1][3:]] if title[1][3].isalnum() else [title[1][4:]]
    #    except IndexError:
    #        logging.info("No sample name was given when submitting")
    #        raise IndexError
    # else:
    #    # Title is not even long enough
    #    logging.info("Title doesn't have enough parts")
    #    raise IndexError

    metadata = MeasurementMetadata.from_title(title, rules)
    # Check that the title had enough components including sample info (no. etc.)
    if metadata.sample_info is None:
        logging.info("No sample name was given when submitting!")
        raise IndexError

    metadata.path = str(folder)
    metadata.manufacturer = Manufacturer.BRUKER
    details_split = details.split()
    metadata.experiment = details_split[0]
    metadata.solvent = details_split[1]

    return metadata


def get_metadata_agilent(folder: Path, rules: MetadataRules) -> MeasurementMetadata:
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

    title = folder.name
    metadata = MeasurementMetadata.from_title(title, rules)
    metadata.path = str(folder)
    metadata.manufacturer = Manufacturer.AGILENT
    metadata.frequency = magnet_freq

    return metadata


def get_metadata(
    folder: Path, rules: MetadataRules, manufacturer: Manufacturer
) -> MeasurementMetadata:
    match manufacturer:
        case Manufacturer.BRUKER:
            return get_metadata_bruker(folder, rules)
        case Manufacturer.AGILENT:
            return get_metadata_agilent(folder, rules)


def generate_folder_name(
    metadata: MeasurementMetadata,
    rules: MetadataRules,
    drop_missing: bool = True,
) -> str:
    """Format folder name according to the prescribed rules."""
    parts = []
    for field in rules.dest_fields:
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
                parts.append(value)
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


#def format_name(
#    folder: Path,
#    metadata: MeasurementMetadata,
#    inc_group: bool = False,
#    inc_init: bool = False,
#    inc_solv: bool = False,
#    nmrcheck_style: bool = False,
#) -> str:
#    """Format folder name according to the user's choices."""
#    # Format in the style of NMRCheck if requested i.e. using underscores,
#    # including initials and spectrometer and date and (spectrometer's) exp no
#    # Note that this is legacy
#    if nmrcheck_style is True:
#        name = "_".join(
#            [
#                x
#                for x in [
#                    metadata.initials,
#                    *(metadata.sample_info),
#                    folder.parent.name,
#                    folder.name,
#                ]
#                if x is not None
#            ]
#        )
#    else:
#        # Include experiment type e.g. proton
#        name = "-".join(
#            [
#                x
#                for x in [
#                    *(metadata.sample_info),
#                    metadata.experiment,
#                ]
#                if x is not None
#            ]
#        )
#    # Apply user choices, some only if NMRCheck style wasn't chosen
#    if nmrcheck_style is False:
#        if inc_init is True and metadata.initials is not None:
#            name = metadata.initials + "-" + name
#        if inc_group is True and metadata.group is not None:
#            name = metadata.group + "-" + name
#    if inc_solv is True and metadata.solvent is not None:
#        name = name + "-" + metadata.solvent
#    # Add frequency info if available
#    if metadata.frequency is not None:
#        name = name + "_" + metadata.frequency
#    # Make sure there are no special characters in the name, and if so, replace them
#    # with the Unicode hexadecimal code points
#    # Otherwise Windows will likely reject them
#    # Replacing rather than just removing ensures the name is still unique compared to
#    # other spectra
#    # alphanumeric characters, space, hyphen, underscore are allowed
#    allowed_symbols = ["-", "_", " "]
#    special = set([x for x in name if not x.isalnum() and x not in allowed_symbols])
#    for x in special:
#        logging.info(f"Char {x} not permitted in spectrum names, replaced with {str(hex(ord(x)))}")
#        name = name.replace(x, str(hex(ord(x))))
#    return name
#
#
#def format_name_admin(
#    folder,
#    metadata: MeasurementMetadata,
#    inc_solv=True,
#    inc_path=False,
#) -> str:
#    """Format folder name in Klaus' desired fashion."""
#    # First do normally but with everything included
#    name = format_name(
#        folder,
#        metadata,
#        inc_group=True,
#        inc_init=True,
#        inc_solv=inc_solv,
#    )
#    # Add location details if requested
#    if inc_path:
#        location = metadata.server_location.replace("/", "_").replace("\\", "_")
#        if inc_path == "before" or inc_path is True:
#            name = location + "_" + name
#        elif inc_path == "after":
#            name = name + "_" + location
#    return name
