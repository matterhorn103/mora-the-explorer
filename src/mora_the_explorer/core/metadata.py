"""Metadata handling."""

from collections.abc import Callable

import datetime
import logging
import re
import tomllib
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Self, TypedDict

import tomli_w

from .spec import Manufacturer


@dataclass
class MatchValues:
    r"""Holds the values that should be inserted into the regex patterns when required.

    Typically the values will want to be user-specified search values and will
    therefore be literal strings. However, as the strings are inserted verbatim
    into regex patterns, regex subpatterns can also be used.

    The default values are wildcard subpatterns, and are appropriate for use in Münster,
    where all user and group identifiers are ASCII letters only and the sample ID
    always starts with a digit (because it begins with the reaction number). Note that
    these default wildcard patterns will only be inserted when the `<var!>` syntax is used;
    for `<var>` a simpler wildcard (`r"\S+"`, matching anything that isn't whitespace)
    is inserted.
    """

    user: str = r"[a-zA-Z]+"
    user2: str = r"[a-zA-Z]+"
    user_name: str = r"[a-zA-Z]+"
    group: str = r"[a-zA-Z]+"
    group_name: str = r"[a-zA-Z]+"
    sample_id: str = r"\d.*"


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
        normalize_sample_id: bool = True,
    ):
        r"""Create a new rules specification.

        The rules are used for two purposes:
        1. Analysing the sample and measurement names, determining whether there
           is a match, and extracting any metadata
        2. Generating a folder name by combining metadata fields

        `sample_pattern` and `measurement_pattern` are regex patterns indicating
        the expected components of the sample and measurement titles respectively.
        They are normal regex in all ways, and use normal regex syntax, with the
        exception of two extensions:

        1. Any occurrence of a backslash-escaped underscore `\_` will be replaced
           by `pattern_sep`, which represents allowed "separator" characters

        2. Variable names surrounded by angle brackets `<var>` are replaced by named
           capture groups `(?P<var>...)`

        The resulting patterns are compiled when the `MeasurementRules` object is
        instantiated, and can be accessed using the `sample_pattern` and
        `measurement_pattern` properties.

        `sample_pattern` is only relevant for Agilent spectrometers, that save the
        spectra organized by sample; rules for Bruker spectrometers should use `None`,
        which is converted to a `.*` wildcard.

        `pattern_sep` is typically a character class. The default value matches
        whitespace, underscores, and hyphens.

        The variable names in angle brackets indicate that some value for a
        metadata variable is expected at that position and so should be extracted
        and stored in a `MeasurementMetadata` object.
        In the ordinary case, a simple wildcard is used (`\S+` i.e. anything other
        than whitespace characters), so `<var>` becomes `(?P<var>\S+)`.

        Through the additional use of `!`, the value of the
        corresponding attribute of `substitutions` can be substituted in.
        Usually the substitued value will be a literal string, and the effect is
        of making that value a hard requirement for a match using the pattern.
        Without `!`, the value may be any number of non-separator characters.

        In combination with `?` in the normal fashion, variables can thus be used
        in the patterns as follows:

        `<var>` – some value for the variable is expected here and should be extracted;
        becomes `(?P<var>\S+)`

        `<var!>` – the corresponding value for the variable is required to match; if `var = "abc"`, becomes `(?P<var>abc)`

        `<var>?` indicates that the variable may or may not be present; becomes `(?P<var>\S+)?`

        `<var!>?` indicates that the variable may or may not be present, but if it is, it must match; becomes e.g. `(?P<var>abc)?`

        If substitution should occur (i.e. `!` is used) then the variable should
        be the name of one of the attributes of `MatchValues`; otherwise,
        the `!` is ignored.

        As the string in `MatchRules` is inserted directly into the pattern, it
        can also be used to specify alternative subpatterns that the respective
        capture groups should match.
        For example, if `values.user = r'[^_]+'`, any occurrences of `<user!>`
        would become `(:P<user>[^_]+)`.
        This provides a convenient mechanism to use different wildcards for each
        of the key variables.

        For Bruker spectra the pattern is matched to the title as recorded in
        `./pdata/1/title`, while for Agilent spectra they are used to analyse the
        names of the sample folder and the contained measurement folders.
        (Note that these are not the only source of a measurement's metadata.)

        `sample_format` and `measurement_format` indicate the desired format of
        the sample and measurement folder names used when a spectrum is saved to
        the destination location. Values of metadata fields are inserted where
        they are indicated in the strings enclosed in curly brackets.
        See `MeasurementMetadata.generate_folder_name()` for more details.

        If `normalize_sample_id` is `True`, it is an indication that all
        underscores and spaces in the sample ID should be replaced by hyphens.
        """

        self.normalize_sample_id = normalize_sample_id
        self.src_sep = pattern_sep
        self.sample_format = sample_format
        self.measurement_format = measurement_format

        # Normalize the substitution values to lowercase now
        # self.substitutions = MatchValues(
        #    **{k: v.casefold() for k, v in asdict(values).items()}
        # )
        # Don't normalize any more because it would ruin regex patterns!
        self.substitutions = values
        if sample_pattern:
            self._sample_pattern = re.compile(self.process_pattern(sample_pattern))
        else:
            self._sample_pattern = re.compile(r".*")
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

        # Replace any variables
        # First those that should just be captured, regardless of value
        wildcard = r"\S+"  # i.e. anything other than whitespace characters
        pattern = re.sub(
            r"<(\w+)>",  # A variable name in angle brackets
            lambda match: f"(?P<{match.group(1)}>{wildcard})",
            pattern,
        )
        # Then those that should be matched literally
        pattern = re.sub(
            r"<(\w+)!>",  # As above but with an exclamation mark
            lambda match: f"(?P<{match.group(1)}>{getattr(self.substitutions, match.group(1))})",
            pattern,
        )

        # A regex pattern that should match `\_` and capture any suffixed repeating characters
        escaped_sep_matching_pattern = r"\\_([*+?]*)"
        # Replace any separators with the separator pattern in a non-capture group
        # Replacing the special `\_` syntax second, after the variables, allows use
        # of `\_` in the substituted values of the variables too
        pattern = re.sub(
            escaped_sep_matching_pattern,
            lambda match: f"(?:{self.src_sep}{match.group(1)})",  # Use a callable lambda to avoid pattern_sep being interpreted (it should be reproduced literally)
            pattern,
        )

        return pattern


METADATA_DTYPES = {
    "path": str,
    "folder_name": str,
    "manufacturer": Manufacturer,
    "submission_time": datetime.datetime,
    "completion_time": datetime.datetime,
    "title": str,
    "sample_id": str,
    "user": str,
    "user2": str,
    "user_name": str,
    "group": str,
    "group_name": str,
    "experiment": str,
    "instrument": str,
    "frequency": float,
    "solvent": str,
    "temperature": int,
    "measurement_no": int,
}


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
    user2: str | None = None
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
    def from_toml(cls, file: Path, ignore_invalid: bool = False) -> "MeasurementMetadata":
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
    def from_measurement_title(
        cls, title: str, rules: MetadataRules
    ) -> "MeasurementMetadata | None":
        """Create a metadata object with the values extracted from `title` according
        to the pattern in `rules`. Returns `None` if the pattern is not matched."""
        # An empty string contains no metadata, obviously, so return early
        if not title:
            return None
        # Get the expected pattern for the title
        pattern: re.Pattern = rules.measurement_pattern
        match: re.Match[str] | None = pattern.fullmatch(title)
        # If the title didn't match the pattern, pass that information on
        if match is None:
            return None
        # Get the values of all the named capture groups (which, for literally
        # matched variables, will be the same as the expected values)
        extracted = match.groupdict()
        converted = {}
        # Convert to the correct types
        for k, v in extracted.items():
            dtype: Callable = METADATA_DTYPES[k]
            if v is None:
                continue
            elif dtype is datetime.datetime:
                converted[k] = datetime.datetime.fromisoformat(v)
            else:
                converted[k] = dtype(v)
        if rules.normalize_sample_id and "sample_id" in converted:
            converted["sample_id"] = converted["sample_id"].replace(" ", "-").replace("_", "-")
        result = MeasurementMetadata(**converted)
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

    def values(
        self, skip_missing: bool = False, default_str: str = ""
    ) -> dict[str, str | int | float | datetime.datetime]:
        """Get a dict of the metadata fields and their values, optionally restricting
        it to only those for which values have been set.

        If `skip_missing` is `False`:
        - any missing string values are replaced with `default_str`.
        - missing `datetime` objects are replaced with `2001-01-01`.
        - missing `int` and `float` values are replaced with `0` and `0.0`"""
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

    def generate_folder_name(self, template: str, missing: str = "") -> str:
        """Get a formatted folder name according to the provided template and
        the available metadata.

        Variables in curly brackets (e.g. `{user}`) in `template` are replaced
        by the value of the respective metadata field.

        The replacement is done by the `str.format()` method, meaning that any
        format specification from Python's "format specification mini-language"
        (https://docs.python.org/3/library/string.html#format-specification-mini-language)
        can be used. For example, a formatted version of the completion time can
        be included using `{completion_time:%y%m%d}`

        If a requested metadata field is missing (i.e. the value of the variable
        is `None`), `missing` is used in its place. With the default value of an
        empty string, this may result in awkward names like `mjm--500-1`, so
        doubled separators ("--", "__") are replaced by a single one.

        Any spaces are normalized by replacement with underscores.
        Additionally, all non-ASCII, non-alphanumerical characters are normalized
        by replacing them with the Unicode code point prefixed with an `"x"`.
        """
        # Substitute variables
        substituted = template.format_map(self.values(skip_missing=False, default_str=missing))
        # Normalize
        normalized = str(substituted).lower()
        # Replace spaces with underscores
        normalized = normalized.replace(" ", "_")
        # Replace runs of separators caused by missing values
        normalized = normalized.replace("--", "-").replace("__", "_")
        # Replace non-ASCII, non-alphanumerical characters
        allowed_symbols = ["-", "_"]
        special = set(
            [
                x
                for x in normalized
                if not x.isascii() or (not x.isalnum() and x not in allowed_symbols)
            ]
        )
        for x in special:
            logging.info(
                f"Char {x} not permitted in folder names, replaced with {str(hex(ord(x)))}"
            )
            normalized = normalized.replace(x, str(hex(ord(x))))
        return normalized


class ParInfo(TypedDict):
    field: str
    dtype: Callable


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

    # This is sadly dependent on the server tree structure and is therefore Münster-specific
    # If there's a parm.txt, it's in there, but that doesn't seem to get saved on
    # the neo400 spectrometers

    if details:
        details_split = details.split()
        metadata.experiment = details_split[0]
        metadata.solvent = details_split[1]

    # The `acqus` file contains everything we need
    # Note that the neo400 files contain more than the av300 ones
    acqus_file = dir / "acqus"
    if acqus_file.exists():
        with open(acqus_file, encoding="utf-8") as f:
            acqus = f.read().splitlines()
        # Contains the parameters, mostly one per line
        # The first few invariables have the format "##PAR= VALUE"
        # Information on the path, user, a timestamp etc. follow on lines that
        # start with "$$ "
        # Subsequent parameter lines have the format "##$PAR= VALUE"
        # Some parameter lines have the format "##$PAR= (0..n)" which indicates
        # that the following line or lines contain a list of `n` space-separated
        # values
        pars: dict[str, ParInfo] = {
            "EXP": {"field": "experiment", "dtype": str},
            "SOLVENT": {"field": "solvent", "dtype": str},
            "SFO1": {"field": "frequency", "dtype": float},
            "TE": {"field": "temperature", "dtype": int},
        }
        # Not always one parameter per line, so have to iterate over all lines
        for line in acqus:
            # We could break once all fields are filled, but the temperature comes
            # at the very bottom of the file, so might as well just save the cost
            # per loop of checking the condition
            # if metadata.frequency and metadata.experiment and metadata.temperature and metadata.completion_time:
            #    # Found everything we need, we can stop iterating
            #    break
            if line.startswith("$$") and "@" in line:
                # Get the date and instrument name
                # Line has the format "$$ 2026-05-11 18:10:02.652 +0200  av1@neo400c"
                split = line.split()
                metadata.instrument = split[-1].split("@")[1]
                # Originally wanted to extract the `DATE` parameter as the timestamp
                # However, `DATE` is a Unix timestamp and therefore requires handling
                # timezones, as the result of converting it to a datetime object is
                # different when the code is run in different timezones.
                # This is contrary to the approach taken otherwise, which is to
                # handle all timestamps as "naive" datetime objects (without tz info)
                # and treat them all as corresponding to the local time at the
                # time of measurement
                iso_timestamp = split[1] + "T" + split[2][:-4]  # Strip the milliseconds
                metadata.completion_time = datetime.datetime.fromisoformat(iso_timestamp)
                continue
            if not line.startswith("##$"):
                continue
            split = line.split("= ")
            par = split[0].removeprefix("##$")
            if par in pars:
                val = split[1]
                if par == "TE":
                    processed_val = int(float(val))
                else:
                    processed_val = pars[par]["dtype"](val.strip("<>"))
                setattr(metadata, pars[par]["field"], processed_val)

    # The only thing that's impossible to get is the submission time, but in Münster
    # we know that (the date, at least) from the folder that it's saved in/the date
    # that is searched for, so we can add that in the calling context

    return metadata


def get_metadata_agilent(dir: Path, rules: MetadataRules) -> MeasurementMetadata | None:
    title = dir.name
    metadata = MeasurementMetadata.from_measurement_title(title, rules)
    if metadata is None:
        # Isn't a match
        return None
    metadata.path = str(dir)
    metadata.folder_name = dir.name
    # This is sadly dependent on the server tree structure and is therefore Münster-specific
    metadata.group_name = dir.parent.parent.parent.name
    metadata.manufacturer = Manufacturer.AGILENT

    procpar_file = dir / "procpar"
    if procpar_file.exists():
        with open(procpar_file, encoding="utf-8") as f:
            procpar = f.read().splitlines()
        # Contains sets of three lines, where the first line starts with the parameter name,
        # and the second line has the value as the second item
        # Specify those which we want to extract and how, with the name of the
        # parameter in the procpar file as the keys
        pars: dict[str, ParInfo] = {
            "kbpslabel": {"field": "experiment", "dtype": str},
            "sfrq": {"field": "frequency", "dtype": float},
            "solvent": {"field": "solvent", "dtype": str},
            "kbspec": {"field": "instrument", "dtype": str},
            "tempk_s": {"field": "temperature", "dtype": int},
            "time_submitted": {
                "field": "submission_time",
                "dtype": datetime.datetime.fromisoformat,
            },
            "time_complete": {"field": "completion_time", "dtype": datetime.datetime.fromisoformat},
        }
        # Turns out we can't rely on the lines being in sets of three, so have
        # to iterate through all of them
        for i, line in enumerate(procpar):
            # We could break once all fields are filled, but the timestamps come
            # pretty near the bottom of the file, so might as well just save the cost
            # per loop of checking the condition
            # if metadata.frequency and metadata.instrument and metadata.solvent and metadata.submission_time and metadata.completion_time:
            #    # Found everything we need, we can stop iterating
            #    break
            try:
                par = line.split()[
                    0
                ]  # Note that for 2 of 3 lines this won't actually be a parameter name
            except IndexError:
                continue
            if par in pars:
                # Value on next line in second position
                val = procpar[i + 1].split()[1]
                processed_val = pars[par]["dtype"](val.strip('"'))
                setattr(metadata, pars[par]["field"], processed_val)

    return metadata


def get_metadata(
    dir: Path,
    rules: MetadataRules,
    manufacturer: Manufacturer,
) -> MeasurementMetadata | None:
    match manufacturer:
        case Manufacturer.BRUKER:
            return get_metadata_bruker(dir, rules)
        case Manufacturer.AGILENT:
            return get_metadata_agilent(dir, rules)
        case _:
            raise ValueError(f"{repr(manufacturer)} is not a valid manufacturer!")
