import datetime
from pathlib import Path

from mora_the_explorer.check.metadata import (
    MetadataRules,
    MeasurementMetadata,
    Manufacturer,
    generate_folder_name,
)
from mora_the_explorer.check.paths import get_check_paths
from .test_config import mock_config


class TestMetadata:
    bruker_rules = MetadataRules(
        {"group": "stu", "user": "mjm"},
        r"<group>*<user>*",
        ["user", "sample_info", "experiment", "solvent"],
    )
    agilent_rules = MetadataRules(
        {"user": "mjm"},
        r"<user>",
        ["user", "sample_info", "experiment", "solvent"],
    )

    def test_bruker_title_extraction(self):
        title = "stu mjm 213-4 repeat"
        metadata = MeasurementMetadata.from_title(title, self.bruker_rules)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            sample_info=["213", "4", "repeat"],
            title=title,
        )

    def test_bruker_name_gen(self):
        metadata = MeasurementMetadata(group="stu", user="mjm", sample_info=["213", "4", "repeat"])
        metadata.manufacturer = Manufacturer.BRUKER
        metadata.date = datetime.date.today()
        name = generate_folder_name(metadata, self.bruker_rules)
        assert name == "mjm-213-4-repeat"

    def test_agilent_title_extraction(self):
        title = "mjm304-1-ß"
        metadata = MeasurementMetadata.from_title(title, self.agilent_rules)
        assert metadata == MeasurementMetadata(
            user="mjm",
            sample_info=["304", "1", "ß"],
            title=title,
        )

    def test_agilent_name_gen(self):
        metadata = MeasurementMetadata(user="mjm", sample_info=["304", "1", "ß"])
        name = generate_folder_name(metadata, self.agilent_rules)
        assert name == "mjm-304-1-0xdf"
    
    def test_no_rules_mutation(self):
        # This is related to the bug tested by `TestExplorer.test_agilent_inconsistent_match_bug()`
        # Only the first of these four was being properly parsed to give user = "akw",
        # because the pattern was being mutated with each use of the rules
        titles = [
            "akw004-4",
            "akw017-3",
            "akw032-2-1",
            "akw17-4",
        ]
        rules = MetadataRules(
            {"user": "akw"},
            r"<user>",
            ["user", "sample_info", "experiment", "solvent"],
        )
        for title in titles:
            metadata = MeasurementMetadata.from_title(title, rules)
            assert metadata.user == "akw"


class TestPaths:
    def test_agilent_path_gen(self):
        config = mock_config()
        spec = "v600"
        spec_info = config.specs[spec]
        check_paths = get_check_paths(
            spec_info,
            Path(config.paths.linux),
            check_date=datetime.date(2023, 10, 15),
            groups={"stu": "studer"},
        )
        print(check_paths)
        assert check_paths[0] == Path(config.paths.linux) / "v600/studer/2023"
