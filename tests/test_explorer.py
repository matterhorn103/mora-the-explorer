from datetime import date
from pathlib import Path
from shutil import rmtree

from mora_the_explorer import Config, Explorer


TEST_DIR = Path(__file__).parent
MOCK_SERVER = TEST_DIR / "mock_server"
MOCK_DEST = TEST_DIR / "nmr"

def empty_folder(path: Path):
    for x in path.iterdir():
        if x.is_file():
            x.unlink()
        elif x.is_dir():
            rmtree(x)


def mock_explorer() -> Explorer:
    mock_app = TEST_DIR / "mock_app_config.toml"
    mock_user = TEST_DIR / "mock_user_config.toml"
    MOCK_DEST.mkdir(exist_ok=True)
    empty_folder(MOCK_DEST)

    config = Config(mock_app, mock_user)
    config.paths.windows = str(MOCK_SERVER)
    config.paths.darwin = str(MOCK_SERVER)
    config.paths.linux = str(MOCK_SERVER)
    config.paths.save = str(MOCK_DEST)

    explorer = Explorer(config)

    return explorer


class TestExplorer:
    def test_init(self):
        explorer = mock_explorer()
        assert len(explorer.config.specs) > 0

    def test_single_check_no_copy(self):
        # Check that a single check executes without issue
        explorer = mock_explorer()
        # Use a fictitious user so we don't match anything
        explorer.config.options.user = "aaa"
        reporter = explorer.single_check(date(2023, 10, 16))
        assert len(reporter.messages()) > 0
        assert len(reporter.copied()) == 0

    def test_single_check_with_copy(self):
        # Check that the spectrum mjm-500-1-proton is found as expected
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        print(reporter.messages())
        assert reporter.messages()[0] == "Spectrum found: mjm-500-1-proton-cdcl3"
        assert reporter.copied()[0] == "mjm-500-1-proton-cdcl3"

    def test_400er_checks_300er(self):
        # Check that checking the neo400 also checks the av300
        explorer = mock_explorer()
        explorer.config.options.spec = "neo400"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        # The spectrum should be found twice but determined to be different spectra,
        # both copied, and automatically numbered as different measurements
        print(reporter.copied())
        assert reporter.copied()[0] == "mjm-500-1-proton-cdcl3"
        assert reporter.copied()[1] == "mjm-500-1-proton-cdcl3-2"

    def test_no_initials(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = False
        explorer.config.options.inc_solvent = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied()[0] == "500-1-proton-cdcl3"

    def test_no_solvent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "av300"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied()[0] == "mjm-500-1-proton"

    def test_agilent(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied()[0] == "mjm-500-1"

    def test_agilent_with_freq(self):
        explorer = mock_explorer()
        explorer.config.options.spec = "v600"
        explorer.config.options.inc_user = True
        explorer.config.options.inc_solvent = False
        explorer.config.options.inc_frequency = True
        reporter = explorer.single_check(date(2023, 10, 15))
        assert reporter.copied()[0] == "mjm-500-1-600"
