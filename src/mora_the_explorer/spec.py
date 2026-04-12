from dataclasses import dataclass, field
from enum import Enum


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


@dataclass
class Spectrometer:
    """Specifies the directory structure and handling behaviour for an single
    spectrometer.

    spec_dir: the path to the folder for the spectrometer, relative to the server
    date: a formatting string that defines <date> - for the format codes see
        https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    check_paths: the paths that should be searched for new spectra
    archives: if spectra from previous years can't be found under check_paths, the
        archive folders are checked in addition
    include: other spectrometers which should be searched at the same time
    manufacturer: the manufacturer of the spectrometer(s)
    display_name: the text shown next to the button in the user interface
        (note that some characters need escaping, e.g. write && for &)
    date_entry: whether the user selects the full date "dd MMM yyyy" or just year "yyyy"
    allow_solvent: whether to enable the folder naming option to include the solvent
    single_check_only: whether users may use multiday and repeat checks for this spec
    restrict_to: the list of groups that should be able to see the spectrometer - if
        this key is not used, the spectrometer will be visible to all
    admin_only: whether the spectrometer should only be chooseable in admin mode

    Possible variable fields in `check_paths` and `archives are:
    - <spec_dir>      (the value of `spec_dir`)
    - <date>          (the value of `date`)
    - <group>         (the chosen group's ID)
    - <group_name>    (the chosen group's name)
    - any strftime formatting string, with % characters, enclosed in <>
    """
    manufacturer: Manufacturer
    display_name: str
    spec_dir: str
    date: str
    date_entry: str
    check_paths: list[str]
    archives: list[str] = field(default_factory=list)
    include: list[str] = field(default_factory=list)
    restrict_to: list[str] = field(default_factory=list)
    allow_solvent: bool = True
    single_check_only: bool = False
    admin_only: bool = False

