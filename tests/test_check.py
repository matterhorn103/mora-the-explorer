import datetime
from pathlib import Path

from mora_the_explorer.core import get_check_paths
from .test_config import mock_config


class TestPaths:
    def test_agilent_path_gen(self):
        config = mock_config()
        spec = "v600"
        spec_info = config.specs[spec]
        check_paths = get_check_paths(
            spec_info,
            Path(config.paths.linux),
            date=datetime.date(2023, 10, 15),
            groups={"stu": "studer"},
        )
        print(check_paths)
        assert check_paths[0] == Path(config.paths.linux) / "v600/studer/2023"
