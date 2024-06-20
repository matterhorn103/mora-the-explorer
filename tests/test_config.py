from pathlib import Path


from mora_the_explorer.explorer import Config


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
        assert config.options["initials"] == "xyz"

    def test_init_user_creation(self):
        # Test if a fresh user config is created for a new user
        if self.new_user.exists():
            self.new_user.unlink()
        config = Config(self.mock_app, self.new_user)
        assert self.new_user.exists()

    def test_init_mock_user(self):
        # Test that options from a (mock) user config are loaded
        config = Config(self.mock_app, self.mock_user)
        assert config.options["initials"] == "mue"

    def test_app_config_replacement(self):
        # Test that app settings from a (mock) user config override the app config
        config = Config(self.mock_app, self.mock_user)
        assert config.groups["new"] == "newgroup"

    def test_init_real_user(self):
        # Test config object creation using the real system user config location
        config = Config(self.mock_app)

    def test_init_real_app_and_user(self):
        # Test config object creation using the proper app config and system user config
        config = Config(self.test_dir.parent / "config.toml")
