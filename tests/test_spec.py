from mora_the_explorer.spec import Manufacturer


class TestManufacturer:
    def test_from_str(self):
        bruker = Manufacturer.from_str("bruker")
        assert bruker == Manufacturer.BRUKER
        bruker_upper = Manufacturer.from_str("Bruker")
        assert bruker_upper == Manufacturer.BRUKER
        agilent = Manufacturer.from_str("agilent")
        agilent_upper = Manufacturer.from_str("Agilent")
        assert agilent == Manufacturer.AGILENT
        assert agilent_upper == Manufacturer.AGILENT
