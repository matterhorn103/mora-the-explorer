from pathlib import Path

from mora_the_explorer import Config, get_rsrc_dir


class TestConfig:
    test_dir = Path(__file__).parent
    mock_app = test_dir / "mock_app_config.toml"
    mock_user = test_dir / "mock_user_config.toml"
    new_user = test_dir / "new_user_config.toml"

    def test_init_no_user(self):
        # Test if the defaults are set according to the (mock) app config
        # Make sure the temp user config doesn't exist yet
        if self.new_user.exists():
            self.new_user.unlink()
        config = Config(self.mock_app, self.new_user)
        assert config.options.user == "mmu"

    def test_init_user_creation(self):
        # Test if a fresh user config is created for a new user
        if self.new_user.exists():
            self.new_user.unlink()
        _config = Config(self.mock_app, self.new_user)
        assert self.new_user.exists()

    def test_init_mock_user(self):
        # Test that options from a (mock) user config are loaded
        config = Config(self.mock_app, self.mock_user)
        assert config.options.user == "mjm"

    def test_app_config_replacement(self):
        # Test that app settings from a (mock) user config override the app config
        config = Config(self.mock_app, self.mock_user)
        assert "new" in config.groups.all
        assert config.groups.all["new"] == "newgroup"
        assert Path(config.paths.linux).expanduser() == Path.home()/"dfs/nmr"
        assert Path(config.paths.save).expanduser() == Path.home()/"nmr"

    def test_init_real_user(self):
        # Test config object creation using the real system user config location
        config = Config(self.mock_app)
        # Note this requires the value to have been changed in your user config!
        assert Path(config.paths.linux).expanduser() == Path.home()/"dfs/nmr"

    def test_init_real_app_and_user(self):
        # Test config object creation using the proper app config and system user config
        _config = Config(get_rsrc_dir() / "config.toml")
