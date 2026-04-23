"""Metadata handling."""

from dataclasses import asdict, dataclass
import datetime
import logging
from pathlib import Path
import re
from typing import Self

import tomli_w

from .spec import Manufacturer


class MetadataRules:
    """Specifies rules for extracting and proliferating measurement metadata, as
    well as the required values for a match."""

    def __init__(
        self,
        conditions: dict[str, str],
        src_pattern: str,
        dest_fields: list[str],
        src_sep: str = r"[\s\-_]",
        dest_sep: str = "-",
    ):
        """Create a new rules specification.

        `conditions` specifies the conditions that are required to be met for
        a measurement to be considered a match for the search. Conditions are
        specified in a `dict` with variable names as the keys and the expected
        values as the values.
        The variable names used should be the same as the field names of
        `MeasurementMetadata`.

        If `sample_info` is not listed as a specific condition, 
        
        Falsey values such as `None` and `""` act as wildcards and cause the
        condition to always be met.
        If a condition is given and the corresponding variable is not even
        present in the metadata, it is not considered a match.
        Matching is done case-insensitively.

        `src_pattern` is a (template for a) regex pattern indicating the expected
        components of the measurement title.
        Variable names surrounded by `<>` or `()` are replaced by capture groups.
        See `MetadataRules.pattern()` for mora details on how `src_pattern` is
        processed before use in matching.
        For Bruker spectra the title is recorded in `./pdata/1/title`, while for
        Agilent spectra it forms the name of the measurement folder.
        (Note that this is not the only source of a measurement's metadata.)

        `dest_fields` indicates the desired metadata fields to include in the
        measurement folder name when it is saved to the destination location.
        See `MeasurementMetadata.generate_folder_name()` for more details.

        `src_sep` should be a regex character class with all the characters that
        should be considered as separators.
        """

        # Normalize the expectation values to lowercase now, and drop any that
        # just have `None` as the value
        self.conditions = {k: v.casefold() for k, v in conditions.items() if v is not None}
        self._src_pattern = src_pattern
        self.src_sep = src_sep
        self.dest_fields = dest_fields
        self.dest_sep = dest_sep

    def pattern(self) -> str:
        """Get the regex that should be used to match the measurement title
        after processing.
        
        `*` and `+` symbols in the regex pattern are replaced by `src_sep` with
        the respective symbol used to indicate how many times the separator is
        expected to be repeated (i.e. `*` means "any number of separator characters"
        and `+` means "at least one separator character"). 
        By default whitespace, hyphens, and underscores are treated as separators.

        Positions where variables should be substituted by their expected values in
        a pre-processing step and matched exactly are indicated in the pattern by
        enclosing them in angle brackets e.g. `<user>`. If a variable's expected
        value is falsey then a wildcard pattern is inserted.
        Capture groups that should be extracted to variables are indicated in
        the pattern by enclosing them in parentheses e.g. `(user)`.
        The variable names used must be ones that are in `conditions`.

        For example:
        
        - If `src_pattern` was `r"<group>*<user>*(sample_info)"` and the default
         `src_sep` was used then the title
          `"stu mjm 213-4 repeat"` would be parsed to give
          `{"group": "stu", "user": "mjm", "sample_info": "213-4 repeat"}`

        - If `src_pattern` was instead `["<user>(sample_info)"]` then the title
          `"mjm304-1"` would be parsed into
          `{"user": "mjm", "sample_info": "304-1"}`
        """
        wildcard = rf"[^\W{self.src_sep.strip("[]")}]+"  # i.e. at least one of any "word" character, but not separator characters
        pattern = self._src_pattern
        logging.debug(pattern)
        # First replace any * or + with the separator pattern in a non-capture group
        pattern = pattern.replace("*", f"(?:{self.src_sep}*)")
        pattern = pattern.replace("+", f"(?:{self.src_sep}+)")

        # Then replace any variables with named capture groups
        # `sample_info` is unlikely to have been given as a condition, so add it
        if "sample_info" not in self.conditions:
            self.conditions["sample_info"] = None
        for variable, expectation in self.conditions.items():
            # If the expectation value is `None` or an empty string, it's a wildcard
            # `sample_info` is allowed to include separators, so it's a different,
            # more general wildcard that matches any characters
            if not expectation:
                expectation = wildcard if variable != "sample_info" else r".*"
            # First those that should be matched literally
            pattern = pattern.replace(f"<{variable}>", f"(?P<{variable}>{expectation})")
            # Then those that should just be captured and compared
            pattern = pattern.replace(f"({variable})", f"(?P<{variable}>{expectation})")

        logging.debug(pattern)
        return pattern


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
    sample_info: str | None = None
    # Access fields programmatically using `getattr(mdata, field)` or `asdict(mdata)`

    @classmethod
    def from_title(cls, title: str, rules: MetadataRules) -> Self | None:
        """Create a metadata object with the values extracted from `title` according
        to the pattern in `rules`. Returns `None` if the pattern is not matched."""
        # An empty string contains no metadata, obviously, so return early
        if not title:
            return None
        # Get the expected pattern for the title
        pattern = rules.pattern()
        match = re.match(pattern, title, re.IGNORECASE)
        # If the title didn't match the pattern, pass that information on
        if match is None:
            return None
        # Get the values of all the named capture groups (which, for literally
        # matched variables, will be the same as the expected values)
        extracted = match.groupdict()
        result = MeasurementMetadata(**extracted)
        # Add the original title too
        result.title = title
        return result

    def matches_rules(self, rules: MetadataRules) -> bool:
        """Check if the metadata match a set of rules.

        If there is a condition for a variable but the expected value given is falsey
        (e.g. `None` or an empty string), any found value at all meets the condition
        and it is considered a match.
        An expected value of `None`, `""`, etc. thus functions as a wildcard.
        
        If the metadata for the variable of a condition was not found (and therefore
        the corresponding variable is still set to `None`), the condition is not
        met and it is not considered a match.

        However, if a condition is given and the variable is not a metadata
        field at all, an `AttributeError` will be raised.

        Matching is done case-insensitively.
        """
        for variable, expectation in rules.conditions.items():
            logging.debug(f"{variable} expected to be {expectation}")
            if not expectation:
                # Any value meets the condition
                continue
            found = getattr(self, variable)
            logging.debug(f"{variable} found to be {found}")
            if found is None:
                # Condition can't be met if metadata wasn't even found, not a match
                return False
            if found.casefold() != expectation:
                # Condition is not met, not a match
                return False
        # All conditions have been met
        return True
    
    def generate_folder_name(
        self,
        rules: MetadataRules,
        drop_missing: bool = True,
    ) -> str:
        """Get a formatted folder name according to the prescribed rules.

        The metadata fields to be included in the name are those in
        `rules.dest_fields`, and the name is constructed by joining the values of
        those fields with the desired separator (specified by `rules.dest_sep`).

        If an item in `rules.dest_fields` is not a variable but a list of variables,
        they are treated as mutually exclusive options and the first variable in the
        sublist with a value will be used. For example, `["user", "user_name"]`
        would be an instruction to "include the `user` field if available, if not,
        include the `user_name` instead".

        If a field begins with `%` it is interpreted as a strftime formatting
        string and the value used is the appropriately formatted component of the
        `date` metadata field.

        If a requested metadata field is missing (i.e. the value of the variable
        is `None`) the string `"unknown"` is used in its place, unless `drop_missing`
        is `True`, in which case the field is simply skipped. The same applies if
        a requested field is not an actual metadata field.
        
        If `sample_info` is to be included (it is listed in `rules.dest_fields`)
        it is normalized so that all instances of `rules.src_sep` become
        `rules.dest_sep`.
        
        Additionally, all non-ASCII, non-alphanumerical characters are normalized
        by replacing them with the Unicode code point prefixed with an `"x"`.

        For example, if the metadata are:
        `{"group": "stu", "user": "mjm", "sample_info": "213-4 repeat", "frequency": "300", "solvent": "DMSO-d6"}`
        and `dest_fields` had the value `["user", "sample_info", "solvent"]`
        then the measurement folder would be saved with the path
        `<dest_path>/mjm-213-4-repeat-DMSO-d6/`
        """
        parts = []
        for field in rules.dest_fields:
            if isinstance(field, list):
                for mutually_exclusive_field in field:
                    if getattr(self, mutually_exclusive_field, None) is not None:
                        field = mutually_exclusive_field
            if field.startswith("%"):
                # strftime formatting strings beginning with `%` are replaced by the
                # appropriately formatted component of the date
                parts.append(self.date.strftime(field))
            else:
                value = getattr(self, field, None)
                if value is not None:
                    if field == "sample_info":
                        # Normalize the separators
                        normalized = re.sub(rules.src_sep, rules.dest_sep, value)
                        parts.append(normalized)
                    else:
                        parts.append(str(value))
                # What do we do if the user wants something in the folder name but
                # we don't have that information?
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
    
    def write_toml(self, file: Path):
        """Write the metadata as TOML to `file`."""

        d = asdict(self)
        # Can't serialize the `Manufacturer` enum as-is
        d["manufacturer"] = str(d["manufacturer"])
        # Remove anything that has a value of `None` (TOML has no null value)
        d = {k: v for k, v in d.items() if v is not None}

        with open(file, "wb") as f:
            tomli_w.dump(d, f)


def get_metadata_bruker(folder: Path, rules: MetadataRules) -> MeasurementMetadata | None:
    # Extract title and experiment details from title file in spectrum folder
    title_file = folder / "pdata/1/title"
    with open(title_file, encoding="utf-8") as f:
        title_contents = f.read().splitlines()
    if len(title_contents) < 2:
        logging.info(f"Title file for {folder} is empty!")
        title = ""
        details = ""
    else:
        title = title_contents[0]
        details = title_contents[1]
        # Make a note if there's the title is empty
        if not title:
            logging.info(f"No measurement title was given for {folder}!")

    metadata = MeasurementMetadata.from_title(title, rules)
    if metadata is None:
        # Isn't a match
        return None
    metadata.path = str(folder)
    metadata.folder_name = folder.name
    metadata.manufacturer = Manufacturer.BRUKER

    if details:
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


def get_metadata_agilent(folder: Path, rules: MetadataRules) -> MeasurementMetadata | None:
    title = folder.name
    metadata = MeasurementMetadata.from_title(title, rules)
    if metadata is None:
        # Isn't a match
        return None
    metadata.path = str(folder)
    metadata.folder_name = folder.name
    metadata.group_name = folder.parent.parent.name
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
