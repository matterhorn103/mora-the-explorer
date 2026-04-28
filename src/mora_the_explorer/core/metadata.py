"""Metadata handling."""

from dataclasses import asdict, dataclass, fields
import datetime
import logging
from pathlib import Path
import re
from typing import Self

import tomli_w

from .spec import Manufacturer


@dataclass
class VariableSubstitutions:
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
        substitutions: VariableSubstitutions,
        measurement_pattern: str,
        dest_fields: list[str],
        pattern_sep: str = r"[\s_-]",
        dest_sep: str = "-",
    ):
        r"""Create a new rules specification.

        The rules are used for two purposes:
        1. Analysing the sample and measurement names, determining whether there
           is a match, and extracting any metadata
        2. Generating a folder name by combining metadata fields

        `measurement_pattern` is a regex pattern indicating the expected
        components of the measurement title. It is a normal regex in all ways,
        and uses normal regex syntax, with the exception of two extensions:

        1. Any occurrence of a backslash-escaped underscore `\_` will be replaced
           by `pattern_sep`, which represents allowed "separator" characters

        2. Variable names surrounded by angle brackets `<var>` are replaced by named
           capture groups `(?P<var>...)`

        The resulting patterns are compiled when the `MeasurementRules` object is
        instantiated, and can be accessed using the `sample_pattern` and
        `measurement_pattern` properties.
        
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
        be the name of one of the attributes of `VariableSubstitutions`; otherwise,
        the `!` is ignored.

        Substituted values are normalized to lowercase using `str.casefold()`.
        
        For Bruker spectra the pattern is matched to the title as recorded in
        `./pdata/1/title`, while for Agilent spectra they are used to analyse the
        names of the sample folder and the contained measurement folders.
        (Note that these are not the only source of a measurement's metadata.)

        `dest_fields` indicates the desired metadata fields to include in the
        measurement folder name when it is saved to the destination location, and
        `dest_sep` the separator character (or string) that should be used to join
        the fields.
        See `MeasurementMetadata.generate_folder_name()` for more details.
        """

        self.src_sep = pattern_sep
        self.dest_fields = dest_fields
        self.dest_sep = dest_sep
        
        # Normalize the substitution values to lowercase now
        self.substitutions = VariableSubstitutions(
            **{k: v.casefold() for k, v in asdict(substitutions).items()}
        )
        self._measurement_pattern = re.compile(self.process_pattern(measurement_pattern))

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
            # First those that should just be captured, whatever they are

            # First see if it should just be captured
            pattern = pattern.replace(f"<{variable}>", f"(?P<{variable}>{wildcard})")
            # Then see if it should be matched literally
            # (Important that the wildcard ones are replaced first)
            pattern = pattern.replace(f"<{variable}!>", f"(?P<{variable}>{value})")

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
    instrument: str | None = None
    frequency: float | None = None
    solvent: str | None = None
    sample_id: str | None = None
    # Access fields programmatically using `getattr(mdata, field)` or `asdict(mdata)`

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
        
        If `sample_id` is to be included (it is listed in `rules.dest_fields`)
        it is normalized so that all instances of `rules.src_sep` become
        `rules.dest_sep`.
        
        Additionally, all non-ASCII, non-alphanumerical characters are normalized
        by replacing them with the Unicode code point prefixed with an `"x"`.

        For example, if the metadata are:
        `{"group": "stu", "user": "mjm", "sample_id": "213-4 repeat", "frequency": "300", "solvent": "DMSO-d6"}`
        and `dest_fields` had the value `["user", "sample_id", "solvent"]`
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
                    if field == "sample_id":
                        # Normalize the separators
                        normalized = re.sub(rules.src_sep, rules.dest_sep, value)
                        parts.append(normalized)
                    elif field == "frequency":
                        # Round it
                        parts.append(str(round(value)) + "mhz")
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
                if metadata.frequency and metadata.instrument:
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
