import datetime

from mora_the_explorer.core import (
    MatchValues,
    MeasurementMetadata,
    MetadataRules,
)
from mora_the_explorer.core.metadata import Manufacturer, get_metadata

from . import MOCK_SERVER

SUBSTITUTIONS = MatchValues(
    group="stu",
    group_name="studer",
    user="mjm",
)

BRUKER_PATTERN = r"<group!>\_*<user_name>?\_*<user!>\_*<user2!>?\_*<sample_id!>"
AGILENT_PATTERN = (
    r"<user!><user2!>?<sample_id!>_(\d{6})_<temperature>k_<experiment>_<measurement_no>\.fid"
)
AGILENT_SAMPLE_PATTERN = r"<user!><sample_id!>"
SAMPLE_FORMAT = "{user}-{sample_id}"
MEASUREMENT_FORMAT = "{user}-{sample_id}_{instrument}_{completion_time:%d%m%y}_{temperature}k_{experiment}_{measurement_no}"

BRUKER_RULES = MetadataRules(
    values=SUBSTITUTIONS,
    sample_pattern=None,
    measurement_pattern=BRUKER_PATTERN,
    sample_format=SAMPLE_FORMAT,
    measurement_format=MEASUREMENT_FORMAT,
)
AGILENT_RULES = MetadataRules(
    values=SUBSTITUTIONS,
    sample_pattern=AGILENT_SAMPLE_PATTERN,
    measurement_pattern=AGILENT_PATTERN,
    sample_format=SAMPLE_FORMAT,
    measurement_format=MEASUREMENT_FORMAT,
)


class TestRules:
    def test_bruker_pattern_processing(self):
        processed = BRUKER_RULES.process_pattern(BRUKER_PATTERN)
        print(processed)
        theoretical = r"(?P<group>stu)(?:[\s_-]*)(?P<user_name>\S+)?(?:[\s_-]*)(?P<user>mjm)(?:[\s_-]*)(?P<user2>[a-zA-Z]+)?(?:[\s_-]*)(?P<sample_id>\d.*)"
        print(theoretical)
        assert processed == theoretical

    def test_agilent_pattern_processing(self):
        processed = AGILENT_RULES.process_pattern(AGILENT_PATTERN)
        print(processed)
        theoretical = r"(?P<user>mjm)(?P<user2>[a-zA-Z]+)?(?P<sample_id>\d.*)_(\d{6})_(?P<temperature>\S+)k_(?P<experiment>\S+)_(?P<measurement_no>\S+)\.fid"
        print(theoretical)
        assert processed == theoretical


class TestMetadata:
    # Tests of extraction from the "title" with each kind of spectrometer
    def test_bruker_title_extraction(self):
        title = "stu mjm 213-4 repeat"
        metadata = MeasurementMetadata.from_measurement_title(title, BRUKER_RULES)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            sample_id="213-4-repeat",
            title=title,
        )

    def test_agilent_title_extraction(self):
        title = "mjm500-1_151023_299k_1h_1.fid"
        metadata = MeasurementMetadata.from_measurement_title(title, AGILENT_RULES)
        print(metadata)
        assert metadata == MeasurementMetadata(
            user="mjm",
            sample_id="500-1",
            temperature=299,
            experiment="1h",
            measurement_no=1,
            title=title,
        )

    # Tests of extraction from an actual measurement folder
    def test_bruker_metadata_extraction(self):
        # This folder has a `title` file and an `acqus` file and its metadata
        # should be complete
        measurement = MOCK_SERVER / "av300/Oct15-2023/200"
        metadata = get_metadata(measurement, BRUKER_RULES, Manufacturer.BRUKER)
        assert metadata == MeasurementMetadata(
            path=str(measurement),
            folder_name=measurement.name,
            manufacturer=Manufacturer.BRUKER,
            submission_time=None,  # Is set separately based on the check date
            completion_time=datetime.datetime(2023, 10, 15, 19, 57, 3),  # 2023-10-15 19:57:03.652
            title="stu mjm 500-1",
            sample_id="500-1",
            user="mjm",
            user_name=None,
            group="stu",
            group_name=None,
            experiment="proton",
            instrument="av300",
            frequency=300.23247159,
            solvent="CDCl3",
            temperature=300,
            measurement_no=None,  # Is set separately based on the path
        )

    def test_agilent_metadata_extraction(self):
        # This folder has a `procpar` and its metadata should be complete
        measurement = MOCK_SERVER / "v600/studer/2023/mjm500-1/mjm500-1_151023_299k_1h_1.fid"
        metadata = get_metadata(measurement, AGILENT_RULES, Manufacturer.AGILENT)
        assert metadata == MeasurementMetadata(
            path=str(measurement),
            folder_name=measurement.name,
            manufacturer=Manufacturer.AGILENT,
            # Submission time and completion time seem to be identical on Agilent specs?
            submission_time=datetime.datetime(2023, 10, 15, 17, 50, 59),  # 20231015T175059
            completion_time=datetime.datetime(2023, 10, 15, 17, 50, 59),  # 20231015T175059
            title="mjm500-1_151023_299k_1h_1.fid",
            sample_id="500-1",
            user="mjm",
            user_name=None,
            group=None,
            group_name="studer",  # Is based on the path, unfortunately
            experiment="1h",
            instrument="v600",
            frequency=599.8324892,
            solvent="cdcl3",
            temperature=299,
            measurement_no=1,
        )

    def test_sample_name_gen(self):
        metadata = MeasurementMetadata(group="stu", user="mjm", sample_id="213-4")
        name = metadata.generate_folder_name(SAMPLE_FORMAT)
        assert name == "mjm-213-4"

    def test_sample_name_gen_disallowed_chars(self):
        metadata = MeasurementMetadata(user="mjm", sample_id="304-1-ß repeat")
        name = metadata.generate_folder_name(SAMPLE_FORMAT)
        # Spaces should be normalized to underscores
        # Characters outside of [a-zA-Z0-9-] should be normalized to hexadecimal Unicode code points
        assert name == "mjm-304-1-0xdf_repeat"

    def test_measurement_name_gen(self):
        metadata = MeasurementMetadata(
            completion_time=datetime.datetime(2026, 3, 23),
            sample_id="17-4",
            user="akw",
            user_name=None,
            group="gil",
            group_name="gilmour",
            experiment="1h",
            instrument="neo400a",
            frequency=300.26,
            solvent="CDCl3",
            temperature=299,
            measurement_no=260,
        )
        name = metadata.generate_folder_name(MEASUREMENT_FORMAT)
        assert name == "akw-17-4_neo400a_230326_299k_1h_260"

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
            MatchValues(user="akw"),
            r"<user!><sample_id!>",
            r"<user!><sample_id!>",
            SAMPLE_FORMAT,
            MEASUREMENT_FORMAT,
        )
        for title in titles:
            metadata = MeasurementMetadata.from_measurement_title(title, rules)
            assert metadata.user == "akw"  # type: ignore

    def test_user2_extraction(self):
        # Bruker first
        title = "stu mjm al 14-1"
        metadata = MeasurementMetadata.from_measurement_title(title, BRUKER_RULES)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            user2="al",
            sample_id="14-1",
            title=title,
        )
        # Check for a likely "mistake" whereby the second user is treated as part of the sample ID
        title = "stu mjm al-14-1"
        metadata = MeasurementMetadata.from_measurement_title(title, BRUKER_RULES)
        assert metadata == MeasurementMetadata(
            group="stu",
            user="mjm",
            user2="al",
            sample_id="14-1",
            title=title,
        )
        # Now Agilent, where there is (annoyingly) no separation between the two user initialisms
        title = "mjmal14-1_151023_299k_1h_1.fid"
        metadata = MeasurementMetadata.from_measurement_title(title, AGILENT_RULES)
        print(metadata)
        assert metadata == MeasurementMetadata(
            user="mjm",
            user2="al",
            sample_id="14-1",
            temperature=299,
            experiment="1h",
            measurement_no=1,
            title=title,
        )

    def test_sample_id_normalization(self):
        values = MatchValues(user="nho", group="glo")
        bruker_rules = MetadataRules(
            values=values,
            sample_pattern=None,
            measurement_pattern=BRUKER_PATTERN,
            sample_format=SAMPLE_FORMAT,
            measurement_format=MEASUREMENT_FORMAT,
        )
        agilent_rules = MetadataRules(
            values=values,
            sample_pattern=AGILENT_SAMPLE_PATTERN,
            measurement_pattern=AGILENT_PATTERN,
            sample_format=SAMPLE_FORMAT,
            measurement_format=MEASUREMENT_FORMAT,
        )
        # Check that the typical formats used for names all give the same end result
        bruker1 = MeasurementMetadata.from_measurement_title("glo nho nb 052-01-1", bruker_rules)  # In common use e.g. by the Studer group
        bruker2 = MeasurementMetadata.from_measurement_title("glo nho nb 052 01 1", bruker_rules)  # Format used by the department themselves on Bruker spectrometers
        bruker3 = MeasurementMetadata.from_measurement_title("glo nho nb-052-01-1", bruker_rules)  # For good measure
        agilent = MeasurementMetadata.from_measurement_title("nhonb052-01-1_130526_299k_1h_1.fid", agilent_rules)
        expectation = "052-01-1"
        assert bruker1.sample_id == expectation
        assert bruker2.sample_id == expectation
        assert bruker3.sample_id == expectation
        assert agilent.sample_id ==  expectation
        # Check that the normalization is correctly controlled by the option
        bruker_rules.normalize_sample_id = False
        bruker_non_normalized = MeasurementMetadata.from_measurement_title("glo nho nb 052 01 1", bruker_rules)
        assert bruker_non_normalized.sample_id != bruker2.sample_id
