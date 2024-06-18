import sys
from datetime import date, timedelta
from pathlib import Path
from shutil import rmtree

import pytest

from mora_the_explorer.explorer import app, Config, Explorer


def empty_folder(path: Path):
    for x in path.iterdir():
        if x.is_file():
            x.unlink()
        elif x.is_dir():
            rmtree(x)


class TestExplorer:

    test_dir = Path(__file__).parent
    config = Config(test_dir.parent / "config.toml")

    def test_init_no_config(self):
        explorer = Explorer()
        assert explorer.config is None
    
    def test_init(self):
        explorer = Explorer(self.config)
        assert len(explorer.specs) > 0
    

class TestCheck:

    test_dir = Path(__file__).parent
    config = Config(test_dir.parent / "config.toml")
    nmr_dest = test_dir / "nmr"
    nmr_dest.mkdir(exist_ok=True)
    config.options["dest_path"] = str(nmr_dest)
    
    def test_single_check_no_copy(self):
        # Check that a single check executes without issue
        output = []
        def completion_handler(copied_list):
            nonlocal output
            output = copied_list
            app.exit()
        config = self.config
        config.options["initials"] = "aaa"
        explorer = Explorer(config)
        explorer.single_check(
            date.today() - timedelta(days=1),
            wild_group=False,
            completion_handler=completion_handler,
        )
        app.exec()
        assert len(output) > 0

    def test_single_check_with_copy(self):
        # Check that the spectrum mjm-500-1-proton is found as expected
        output = []
        empty_folder(self.nmr_dest)
        def completion_handler(copied_list):
            nonlocal output
            output = copied_list
            app.exit()
        config = self.config
        config.options["initials"] = "mjm"
        config.options["spec"] = "300er"
        config.options["inc_init"] = True
        config.options["inc_solv"] = True
        explorer = Explorer(config)
        explorer.single_check(
            date(2023, 10, 16),
            wild_group=False,
            completion_handler=completion_handler,
        )
        app.exec()
        assert output[1] == "Spectrum found: mjm-500-1-proton-DMSO"

    def test_400er_checks_300er(self):
        # Check that checking the 400er also checks the 300er
        output = []
        empty_folder(self.nmr_dest)
        def completion_handler(copied_list):
            nonlocal output
            output = copied_list
            app.exit()
        config = self.config
        config.options["initials"] = "mjm"
        config.options["spec"] = "400er"
        config.options["inc_init"] = True
        config.options["inc_solv"] = True
        explorer = Explorer(config)
        explorer.single_check(
            date(2023, 10, 16),
            wild_group=False,
            completion_handler=completion_handler,
        )
        app.exec()
        assert output[1] == "Spectrum found: mjm-500-1-proton-DMSO"

    def test_no_initials(self):
        output = []
        empty_folder(self.nmr_dest)
        def completion_handler(copied_list):
            nonlocal output
            output = copied_list
            app.exit()
        config = self.config
        config.options["initials"] = "mjm"
        config.options["spec"] = "300er"
        config.options["inc_init"] = False
        config.options["inc_solv"] = True
        explorer = Explorer(config)
        explorer.single_check(
            date(2023, 10, 16),
            wild_group=False,
            completion_handler=completion_handler,
        )
        app.exec()
        assert output[1] == "Spectrum found: 500-1-proton-DMSO"

    def test_no_solvent(self):
        output = []
        empty_folder(self.nmr_dest)
        def completion_handler(copied_list):
            nonlocal output
            output = copied_list
            app.exit()
        config = self.config
        config.options["initials"] = "mjm"
        config.options["spec"] = "300er"
        config.options["inc_init"] = True
        config.options["inc_solv"] = False
        explorer = Explorer(config)
        explorer.single_check(
            date(2023, 10, 16),
            wild_group=False,
            completion_handler=completion_handler,
        )
        app.exec()
        assert output[1] == "Spectrum found: mjm-500-1-proton"

