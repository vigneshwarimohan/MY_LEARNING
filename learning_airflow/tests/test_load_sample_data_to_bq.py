import unittest
from unittest.mock import Mock

from scripts.load_sample_data_to_bq import ensure_dataset_exists


class EnsureDatasetExistsTests(unittest.TestCase):
    def test_creates_dataset_when_missing(self):
        client = Mock()
        client.get_dataset.side_effect = Exception("missing")

        ensure_dataset_exists(client, "demo-project", "learning_dataset", "US")

        client.create_dataset.assert_called_once()

    def test_skips_creation_when_dataset_exists(self):
        client = Mock()
        client.get_dataset.return_value = object()

        ensure_dataset_exists(client, "demo-project", "learning_dataset", "US")

        client.create_dataset.assert_not_called()


if __name__ == "__main__":
    unittest.main()
