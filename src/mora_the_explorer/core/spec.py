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

    def __str__(self) -> str:
        match self:
            case Manufacturer.BRUKER:
                return "bruker"
            case Manufacturer.AGILENT:
                return "agilent"


@dataclass
class Spectrometer:
    """A profile describing the directory structure and handling behaviour for a
    spectrometer or a group of spectrometers that should be searched together.

    manufacturer: the manufacturer of the spectrometer(s)
    display_name: the text shown next to the button in the user interface
        (note that some characters need escaping, e.g. write && for &)
    sample_pattern: the expected fields in the sample folder name (Agilent only)
    measurement_pattern: the expected fields in the measurement title
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

    Possible variable fields in `check_paths` and `archives` are:
    - <user>          (the user's ID)
    - <user_name>     (the user's name)
    - <group>         (the chosen group's ID)
    - <group_name>    (the chosen group's name)
    - any strftime formatting string, with % characters, enclosed in {}
    - for the format codes see https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    """

    manufacturer: Manufacturer
    display_name: str
    measurement_pattern: str
    date_entry: str
    check_paths: list[str]
    archives: list[str] = field(default_factory=list)
    include: list[Self | str] = field(default_factory=list)
    sample_pattern: str | None = None
    restrict_to: list[str] = field(default_factory=list)
    admin_only: bool = False
    single_check_only: bool = False
