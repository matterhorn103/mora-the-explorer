"""Metadata handling."""

from dataclasses import asdict, dataclass, fields
import datetime
import logging
from pathlib import Path
import re
import tomllib
from typing import Self

import tomli_w

from .spec import Manufacturer


@dataclass
class MatchValues:
    """Holds the values that should be inserted into the regex patterns when required."""

    user: str
    user_name: str
    group: str
    group_name: str
    sample_id: str


class MetadataRules:
    """Specifies rules for extracting and proliferating measurement metadata, as
    well as the required values for a match."""

    def __init__(
        self,
        values: MatchValues,
        sample_pattern: str | None,
        measurement_pattern: str,
        sample_format: str,
        measurement_format: str,
        pattern_sep: str = r"[\s_-]",
    ):
        r"""Create a new rules specification.

        The rules are used for two purposes:
        1. Analysing the sample and measurement names, determining whether there
           is a match, and extracting any metadata
        2. Generating a folder name by combining metadata fields

        `sample_pattern` and `measurement_pattern` are regex patterns indicating
        the expected components of the sample and measurement titles respectively.
        It is a normal regex in all ways, and uses normal regex syntax, with the
        exception of two extensions:

        1. Any occurrence of a backslash-escaped underscore `\_` will be replaced
           by `pattern_sep`, which represents allowed "separator" characters

        2. Variable names surrounded by angle brackets `<var>` are replaced by named
           capture groups `(?P<var>...)`

        The resulting patterns are compiled when the `MeasurementRules` object is
        instantiated, and can be accessed using the `sample_pattern` and
        `measurement_pattern` properties.

        `sample_pattern` is only relevant for Agilent spectrometers, that save the
        spectra organized by sample; rules for Bruker spectrometers should use `None`.
        
        `pattern_sep` is typically a character class. The default value matches
        whitespace, underscores, and hyphens.

        The capture groups indicate that some value for a metadata variable is
        expected at that position and so should be extracted and stored in a
        `MeasurementMetadata` object. Through the use of `!`, the value of the
        corresponding attribute of `substitutions` can be substituted in.
        Usually the substitued value will be a literal string, and the effect is
        of making that value a hard requirement for a match using the pattern.
        Without `!`, the value may be any number of non-separator characters.

        In combination with `?` in the normal fashion, variables can thus be used
        in the patterns as follows:

        `<var>` – some value for the variable is expected here and should be extracted;
        becomes `(?P<var>[^\_]+)`

        `<var!>` – the corresponding value for the variable is required to match; if `var = "abc"`, becomes `(?P<var>abc)`
        
        `<var>?` indicates that the variable may or may not be present; becomes `(?P<var>[^\_]+)?`
        
        `<var!>?` indicates that the variable may or may not be present, but if it is, it must match; becomes e.g. `(?P<var>abc)?`

        If substitution should occur (i.e. `!` is used) then the variable should
        be the name of one of the attributes of `MatchValues`; otherwise,
        the `!` is ignored.

        Substituted values are normalized to lowercase using `str.casefold()`.
        
        For Bruker spectra the pattern is matched to the title as recorded in
        `./pdata/1/title`, while for Agilent spectra they are used to analyse the
        names of the sample folder and the contained measurement folders.
        (Note that these are not the only source of a measurement's metadata.)

        `sample_format` and `measurement_format` indicate the desired format of
        the sample and measurement folder names used when a spectrum is saved to
        the destination location. Values of metadata fields are inserted where
        they are indicated in the strings enclosed in curly brackets.
        See `MeasurementMetadata.generate_folder_name()` for more details.
        """

        self.src_sep = pattern_sep
        self.sample_format = sample_format
        self.measurement_format = measurement_format
        
        # Normalize the substitution values to lowercase now
        self.substitutions = MatchValues(
            **{k: v.casefold() for k, v in asdict(values).items()}
        )
        if sample_pattern:
            self._sample_pattern = re.compile(self.process_pattern(sample_pattern))
        else:
            self._sample_pattern = sample_pattern
        self._measurement_pattern = re.compile(self.process_pattern(measurement_pattern))
    
    @property
    def sample_pattern(self) -> re.Pattern:
        """Get the processed regex that should be used to match the sample title."""
        return self._sample_pattern

    @property
    def measurement_pattern(self) -> re.Pattern:
        """Get the processed regex that should be used to match the measurement title."""
        return self._measurement_pattern

    def process_pattern(self, pattern: str) -> str:
        """Process any use of the custom extensions in the regex pattern based on the
        provided `pattern_sep` and `substitutions`."""

        # A regex pattern that should match `\_` and capture any suffixed repeating characters
        escaped_sep_matching_pattern = r'\\_([*+?]*)'
        # Replace any separators with the separator pattern in a non-capture group
        pattern = re.sub(
            escaped_sep_matching_pattern,
            lambda match: f'(?:{self.src_sep}{match.group(1)})',  # Use a callable lambda to avoid pattern_sep being interpreted (it should be reproduced literally)
            pattern,
        )

        normal_wildcard = rf'[^{self.src_sep.strip("[]")}]+'  # i.e. anything other than separator characters
        # `sample_id` is allowed to include separators, so it's a different,
        # more general wildcard that matches any characters
        sample_id_wildcard = r".*"
        for variable, value in asdict(self.substitutions).items():
            wildcard = sample_id_wildcard if variable == "sample_id" else normal_wildcard
            # First see if it should just be captured, regardless of value
            pattern = pattern.replace(f"<{variable}>", f"(?P<{variable}>{wildcard})")
            # Then see if it is required to match literally
            # (Important that the wildcard ones are replaced first)
            pattern = pattern.replace(f"<{variable}!>", f"(?P<{variable}>{value})")

        return pattern


@dataclass
class MeasurementMetadata:
    """The actual extracted metadata of a measurement."""

    path: str | None = None
    folder_name: str | None = None
    manufacturer: Manufacturer | None = None
    submission_time: datetime.datetime | None = None
    completion_time: datetime.datetime | None = None
    title: str | None = None
    sample_id: str | None = None
    user: str | None = None
    user_name: str | None = None
    group: str | None = None
    group_name: str | None = None
    experiment: str | None = None
    instrument: str | None = None
    frequency: float | None = None
    solvent: str | None = None
    temperature: int | None = None
    measurement_no: int | None = None

    @classmethod
    def from_toml(cls, file: Path, ignore_invalid: bool = False) -> Self:
        """Read the metadata from a TOML file.
        
        If `ignore_invalid` is `True`, any fields in the file that are not (currently)
        valid attributes of the dataclass are just ignored; otherwise, their presence
        results in a `TypeError`.
        """

        with open(file, "rb") as f:
            d = tomllib.load(f)
        # Manufacturer has to be converted from a string
        if "manufacturer" in d:
            d["manufacturer"] = Manufacturer.from_str(d["manufacturer"])
        if ignore_invalid:
            valid_fields = [f.name for f in fields(MeasurementMetadata)]
            d = {k: v for k, v in d.items() if k in valid_fields}
        metadata = MeasurementMetadata(**d)
        return metadata

    @classmethod
    def from_measurement_title(cls, title: str, rules: MetadataRules) -> Self | None:
        """Create a metadata object with the values extracted from `title` according
        to the pattern in `rules`. Returns `None` if the pattern is not matched."""
        # An empty string contains no metadata, obviously, so return early
        if not title:
            return None
        # Get the expected pattern for the title
        pattern: re.Pattern = rules.measurement_pattern
        match = pattern.fullmatch(title)
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

    def fields(self, skip_missing: bool = False) -> list[str]:
        """Get a list of the possible metadata fields, optionally restricting it
        to only those for which values have been set.
        
        Note that this method intentionally differs in behaviour from that of
        `dataclasses.fields(MeasurementMetadata)`.
        """
        if skip_missing:
            return [k for k, v in asdict(self).items() if v is not None]
        else:
            return [f.name for f in fields(self)]
    
    def values(self, skip_missing: bool = False, default_str: str = "unknown") -> dict[str, str]:
        """Get a dict of the metadata fields and their values, optionally restricting
        it to only those for which values have been set.

        If `skip_missing` is `False`:
        - any missing string values are replaced with `default_str`.
        - missing `datetime` objects are replaced with `2001-01-01`.
        - missing `int` and `float` values are replaced with `0` and `0.0`
        """
        if skip_missing:
            return {k: v for k, v in asdict(self).items() if v is not None}
        else:
            output = {}
            for k, v in asdict(self).items():
                if v is not None:
                    output[k] = v
                # Datetime objects
                elif k in {"submission_time", "completion_time"}:
                    output[k] = datetime.datetime(2001, 1, 1)
                # Integers
                elif k in {"temperature", "measurement_no"}:
                    output[k] = 0
                # Floats
                elif k in {"frequency"}:
                    output[k] = 0.0
                # String values
                else:
                    output[k] = default_str
            return output
    
    def write_toml(self, file: Path):
        """Write the metadata as TOML to `file`."""

        d = asdict(self)
        # Can't serialize the `Manufacturer` enum as-is
        d["manufacturer"] = str(d["manufacturer"]) if d["manufacturer"] else None
        # Remove anything that has a value of `None` (TOML has no null value)
        d = {k: v for k, v in d.items() if v is not None}

        with open(file, "wb") as f:
            tomli_w.dump(d, f)

    def generate_folder_name(
        self,
        template: str,
        default: str = "unknown",
    ) -> str:
        """Get a formatted folder name according to the provided template and
        the available metadata.

        The name is generated using `rules.sample_format` or
        `rules.measurement_format` as the template as appropriate according to
        the value of `sample`.
        
        Variables in curly brackets (e.g. `{user}`) are replaced by the value of
        the respective metadata field.

        The replacement is done by the `str.format()` method, meaning that any
        format specification from Python's "format specification mini-language"
        (https://docs.python.org/3/library/string.html#format-specification-mini-language)
        can be used. For example, a formatted version of the completion time can
        be included using `{completion_time:%y%m%d}`

        If a requested metadata field is missing (i.e. the value of the variable
        is `None`), `default` is used in its place.
        
        Any spaces are normalized by replacement with underscores.
        Additionally, all non-ASCII, non-alphanumerical characters are normalized
        by replacing them with the Unicode code point prefixed with an `"x"`.
        """
        # Substitute variables
        substituted = template.format_map(self.values(skip_missing=False, default_str=default))
        # Normalize
        normalized = str(substituted).lower()
        # Replace spaces with underscores
        normalized = normalized.replace(" ", "_")
        # Replace non-ASCII, non-alphanumerical characters
        allowed_symbols = ["-", "_"]
        special = set(
            [x for x in normalized if not x.isascii() or (not x.isalnum() and x not in allowed_symbols)]
        )
        for x in special:
            logging.info(f"Char {x} not permitted in folder names, replaced with {str(hex(ord(x)))}")
            normalized = normalized.replace(x, str(hex(ord(x))))
        return normalized


def get_metadata_bruker(dir: Path, rules: MetadataRules) -> MeasurementMetadata | None:
    # Extract title and experiment details from title file in spectrum folder
    title_file = dir / "pdata/1/title"
    if not title_file.exists():
        logging.info(f"No title file for {dir} – presumably not a measurement")
        return None
    with open(title_file, encoding="utf-8") as f:
        title_contents = f.read().splitlines()
    if len(title_contents) < 2:
        logging.info(f"Title file for {dir} is empty!")
        title = ""
        details = ""
    else:
        title = title_contents[0]
        details = title_contents[1]
        # Make a note if the title is empty
        if not title:
            logging.info(f"No measurement title was given for {dir}!")

    logging.debug(title)
    metadata = MeasurementMetadata.from_measurement_title(title, rules)
    if metadata is None:
        # Isn't a match
        return None
    metadata.path = str(dir)
    metadata.folder_name = dir.name
    metadata.manufacturer = Manufacturer.BRUKER

    if details:
        details_split = details.split()
        metadata.experiment = details_split[0]
        metadata.solvent = details_split[1]

    # Get magnet frequency and instrument name
    uxnmr_info_file = dir / "uxnmr.info"
    if uxnmr_info_file.exists():
        with open(uxnmr_info_file, encoding="utf-8") as f:
            for line in f:
                if line.startswith("1H-frequency"):
                    # Line has format "1H-frequency : 300.26 MHz"
                    metadata.frequency = float(line.split()[2])
                if line.startswith("Host"):
                    # Line has format "Host         : av300"
                    metadata.instrument = line.split()[2]
                if line.startswith("Date"):
                    # TODO Work out if this is a reliable source and if this timestamp
                    # actually is for the completion time or not?
                    # Line has format "Date         : Mon Oct 14 14:38:13 2024"
                    metadata.completion_time = datetime.datetime.strptime(
                        line.rstrip(),
                        "Date         : %a %b %d %H:%M:%S %Y",
                    )
                if metadata.frequency and metadata.instrument and metadata.completion_time:
                    # Found everything we need, we can stop iterating
                    break

    return metadata


def get_metadata_agilent(dir: Path, rules: MetadataRules) -> MeasurementMetadata | None:
    title = dir.name
    metadata = MeasurementMetadata.from_measurement_title(title, rules)
    if metadata is None:
        # Isn't a match
        return None
    metadata.path = str(dir)
    metadata.folder_name = dir.name
    metadata.group_name = dir.parent.parent.parent.name
    metadata.manufacturer = Manufacturer.AGILENT
    # One folder contains multiple measurements TODO Extract properly
    metadata.experiment = "various"

    procpar_file = dir / "procpar"
    if procpar_file.exists():
        with open(procpar_file, encoding="utf-8") as f:
            procpar = f.read().splitlines()
        # Contains sets of three lines, where the first line starts with the parameter name,
        # and the second line has the value as the second item
        # Specify those which we want to extract and how, with the name of the
        # parameter in the procpar file as the keys
        pars = {
            "kbpslabel": {"field": "experiment", "dtype": str},
            "sfrq": {"field": "frequency", "dtype": float},
            "solvent": {"field": "solvent", "dtype": str},
            "kbspec": {"field": "instrument", "dtype": str},
            "tempk_s": {"field": "temperature", "dtype": int},
            "time_submitted": {"field": "submission_time", "dtype": datetime.datetime},
            "time_complete": {"field": "completion_time", "dtype": datetime.datetime},
        }
        # Turns out we can't rely on the lines being in sets of three, so have
        # to iterate through all of them
        for i, line in enumerate(procpar):
            try:
                par = line.split()[0]  # Note that for 2 of 3 lines this won't actually be a parameter name
            except IndexError:
                continue
            if par in pars:
                # Value on next line in second position
                val = procpar[i + 1].split()[1]
                processed_val = pars[par]["dtype"](val.strip('"'))
                setattr(metadata, pars[par]["field"], processed_val)
            if metadata.frequency and metadata.instrument and metadata.solvent:
                # Found everything we need, we can stop iterating
                break

    return metadata


def get_metadata(
    dir: Path, rules: MetadataRules, manufacturer: Manufacturer
) -> MeasurementMetadata:
    match manufacturer:
        case Manufacturer.BRUKER:
            return get_metadata_bruker(dir, rules)
        case Manufacturer.AGILENT:
            return get_metadata_agilent(dir, rules)
        case _:
            raise ValueError(f"{repr(manufacturer)} is not a valid manufacturer!")
