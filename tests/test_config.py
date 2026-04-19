from pathlib import Path

from mora_the_explorer import Config, get_rsrc_dir

from . import TEST_DIR, MOCK_APP_CONFIG, mock_config


MOCK_NEW_CONFIG = TEST_DIR / "new_user_config.toml"


def fresh_config(app_config_file: Path = MOCK_APP_CONFIG) -> Config:
    """Simulates the situation where no user config yet exists and so a fresh one
    is created with the default settings from the given app config and not the values
    in the mock user config.
    """
    # Make sure the temp user config doesn't exist yet
    if MOCK_NEW_CONFIG.exists():
        MOCK_NEW_CONFIG.unlink()
    return Config(app_config_file, MOCK_NEW_CONFIG)

class TestConfig:
    def test_init_no_user(self):
        # Test if the defaults are set according to the (mock) app config
        config = fresh_config()
        assert config.options.user == "mmu"

    def test_init_user_creation(self):
        # Test if a fresh user config is created for a new user
        # Make sure the temp user config doesn't exist yet
        if MOCK_NEW_CONFIG.exists():
            MOCK_NEW_CONFIG.unlink()
        assert not MOCK_NEW_CONFIG.exists()
        config = fresh_config()
        assert config.options.user == "mmu"
        assert MOCK_NEW_CONFIG.exists()

    def test_init_mock_user(self):
        # Test that options from a (mock) user config are loaded
        config = mock_config()
        # Groups in user config should supplement, not replace, those in app config
        assert "new" in config.groups.all
        assert config.groups.all["new"] == "newgroup"

    def test_app_config_replacement(self):
        # Test that app settings from a (mock) user config override the app config
        config = mock_config()
        assert config.options.user == "mjm"  # App config has "mmu", user config has "mjm"
        assert Path(config.paths.linux).expanduser() == Path.home()/"dfs/nmr"  # App config has "~/usershare/projects/q_nmr-oc/nmr"
        assert Path(config.paths.save).expanduser() == Path.home()/"nmr"  # App config has "~/Documents/nmr"

    def test_init_real_app_and_user(self):
        # Test config object creation using the proper app config and a fresh user config
        config = fresh_config(get_rsrc_dir() / "config.toml")
        assert "rav" in config.groups.all  # Mock app config only has "gil", "glo", "stu", "biochemie", "pharmazie"


class TestGroups:
    def test_all(self):
        config = mock_config()
        assert config.groups.all == {
            "new": "newgroup",  # The one specified in the mock user config
            "gil": "gilmour",
            "glo": "glorius",
            "stu": "studer",
            "biochemie": "biochemie",
            "pharmazie": "pharmazie",
        }

    def test_overflow(self):
        config = mock_config()
        assert config.groups.overflow == ["biochemie", "pharmazie"]

    def test_filter_no_overflow(self):
        config = mock_config()
        assert config.groups.filter_overflow(False) == {
            "new": "newgroup",  # The one specified in the mock user config
            "gil": "gilmour",
            "glo": "glorius",
            "stu": "studer",
        }
    
    def test_filter_overflow(self):
        config = mock_config()
        assert config.groups.filter_overflow(True) == {
            "biochemie": "biochemie",
            "pharmazie": "pharmazie",
        }
