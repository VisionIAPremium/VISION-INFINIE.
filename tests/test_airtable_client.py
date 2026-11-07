import json
import os
import unittest
from unittest.mock import patch

from core.integrations.airtable.client import (
    AirtableConfigurationError,
    AirtableReadOnlyClient,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class AirtableClientTests(unittest.TestCase):
    def test_requires_base_id(self):
        client = AirtableReadOnlyClient(token="test-token")
        with self.assertRaises(AirtableConfigurationError):
            client.list_records("Content Pipeline")

    def test_requires_token_before_network(self):
        client = AirtableReadOnlyClient("appExampleBase123", token="")
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(AirtableConfigurationError):
                client.list_records("Content Pipeline")

    def test_reads_records_with_bearer_auth(self):
        client = AirtableReadOnlyClient("appExampleBase123", token="test-token")
        payload = {"records": [{"id": "rec1", "fields": {"Title": "Demo"}}]}
        with patch("core.integrations.airtable.client.urlopen",
                   return_value=FakeResponse(payload)) as mocked:
            records = client.list_records("Content Pipeline")
        self.assertEqual(records[0]["id"], "rec1")
        request = mocked.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    def test_pagination_is_bounded(self):
        client = AirtableReadOnlyClient("appExampleBase123", token="test-token")
        pages = [
            {"records": [{"id": "1"}], "offset": "next-page"},
            {"records": [{"id": "2"}], "offset": "third-page"},
        ]
        with patch("core.integrations.airtable.client.urlopen",
                   side_effect=[FakeResponse(pages[0]), FakeResponse(pages[1])]):
            records = client.list_records("Content Pipeline", max_pages=2)
        self.assertEqual([item["id"] for item in records], ["1", "2"])

    def test_page_limits_are_validated(self):
        client = AirtableReadOnlyClient("appExampleBase123", token="test-token")
        with self.assertRaises(ValueError):
            client.list_records("Content Pipeline", max_pages=11)


if __name__ == "__main__":
    unittest.main()
