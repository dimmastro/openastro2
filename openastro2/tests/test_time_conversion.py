import unittest
from openastro2.openastromod.utils import decHourJoin, decHour

class TestTimeConversion(unittest.TestCase):
    """Test suite for decimal hour <-> HMS conversion functions."""

    def test_full_day_conversion_roundtrip(self):
        """Test that converting (h, m, s) -> decimal hour -> (h, m, s) returns original values for all times in a day."""

        total_tested = 0
        errors = []

        for hour in range(24):
            for minute in range(60):
                for second in range(60):
                    total_tested += 1
                    original = (hour, minute, second)

                    # Convert to decimal hour
                    dec_h = decHourJoin(hour, minute, second)

                    # Convert back to HMS
                    converted = tuple(decHour(dec_h))

                    # Assert equality
                    if original != converted:
                        errors.append((original, dec_h, converted))

        # If any errors, print first 10 for debugging
        if errors:
            print(f"\nFound {len(errors)} conversion errors (showing first 10):")
            for orig, dec, conv in errors[:10]:
                print(f"Failed: {orig[0]:02d}:{orig[1]:02d}:{orig[2]:02d} -> "
                      f"dec={dec:.9f} -> {conv[0]:02d}:{conv[1]:02d}:{conv[2]:02d}")

        # Final assertion
        self.assertEqual(
            len(errors), 0,
            f"Conversion roundtrip failed for {len(errors)} out of {total_tested} times."
        )

        print(f"\n✅ Successfully verified {total_tested} time conversions.")


if __name__ == '__main__':
    unittest.main()