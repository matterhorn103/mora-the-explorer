from datetime import datetime

from mora_the_explorer.check.metadata import MetadataRules, MeasurementMetadata, Manufacturer, generate_folder_name


class TestCheck:

    bruker_rules = MetadataRules(
        ["group", "user:3"],
        {"group": "stu", "user": "mjm"},
        ["user", "sample_info", "experiment", "solvent"],
    )
    agilent_rules = MetadataRules(
        ["user:3"],
        {"user": "mjm"},
        ["user", "sample_info", "experiment", "solvent"],
    )

    def test_bruker_title_extraction(self):
        title = "stu mjm 213-4 repeat"
        metadata = MeasurementMetadata.from_title(title, self.bruker_rules)
        assert metadata == MeasurementMetadata(
            group="stu", user="mjm", sample_info=["213", "4", "repeat"]
        )
    
    def test_bruker_name_gen(self):
        metadata = MeasurementMetadata(
            group="stu", user="mjm", sample_info=["213", "4", "repeat"]
        )
        metadata.manufacturer = Manufacturer.BRUKER
        metadata.date = datetime.today()
        name = generate_folder_name(metadata, self.bruker_rules)
        assert name == "mjm-213-4-repeat"

    def test_agilent_title_extraction(self):
        title = "mjm304-1-ß"
        metadata = MeasurementMetadata.from_title(title, self.agilent_rules)
        assert metadata == MeasurementMetadata(user="mjm", sample_info=["304", "1", "ß"])
    
    def test_agilent_name_gen(self):
        metadata = MeasurementMetadata(user="mjm", sample_info=["304", "1", "ß"])
        name = generate_folder_name(metadata, self.agilent_rules)
        assert name == "mjm-304-1-0xdf"
