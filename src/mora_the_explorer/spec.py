from dataclasses import dataclass, field
from enum import Enum
from typing import Self


class Manufacturer(Enum):
    BRUKER = 1
    AGILENT = 2

    @classmethod
    def from_str(cls, s: str) -> Self:
        if s.lower() == "bruker":
            return Manufacturer.BRUKER
        elif s.lower() == "agilent":
            return Manufacturer.AGILENT
        else:
            raise ValueError("Only Bruker and Agilent are recognized manufacturers!")


@dataclass
class Spectrometer:
    """A profile describing the directory structure and handling behaviour for a
    spectrometer or a group of spectrometers that should be searched together.

    manufacturer: the manufacturer of the spectrometer(s)
    display_name: the text shown next to the button in the user interface
        (note that some characters need escaping, e.g. write && for &)
    spec_dir: the path to the folder for the spectrometer, relative to the server
    title_format: the expected fields in the measurement title
    match_metadata: the metadata fields that should be considered as conditions
        for a match (order is irrelevant)
    date: a formatting string that defines <date> - for the format codes see
        https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    date_entry: whether the user selects the full date "dd MMM yyyy" or just year "yyyy"
    check_paths: the paths that should be searched for new spectra
    archives: if spectra from previous years can't be found under check_paths, the
        archive folders are checked in addition
    include: other spectrometers which should be searched at the same time
    restrict_to: the list of groups that should be able to see the spectrometer - if
        this key is not used, the spectrometer will be visible to all
    admin_only: whether the spectrometer should only be chooseable in admin mode
    allow_solvent: whether to enable the folder naming option to include the solvent
    single_check_only: whether users may use multiday and repeat checks for this spec

    Possible variable fields in `check_paths` and `archives are:
    - <spec_dir>      (the value of `spec_dir`)
    - <date>          (the value of `date`)
    - <group>         (the chosen group's ID)
    - <group_name>    (the chosen group's name)
    - any strftime formatting string, with % characters, enclosed in {}
    """

    manufacturer: Manufacturer
    display_name: str
    spec_dir: str
    title_format: list[str]
    match_metadata: list[str]
    date: str
    date_entry: str
    check_paths: list[str]
    archives: list[str] = field(default_factory=list)
    include: list[Self | str] = field(default_factory=list)
    restrict_to: list[str] = field(default_factory=list)
    admin_only: bool = False
    single_check_only: bool = False
