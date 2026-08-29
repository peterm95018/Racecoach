from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from racecoach.clokkr import (
    build_results_request,
    classify_clokkr_run,
    discover_event_ids,
    fetch_driver_result,
    parse_results_jsonl,
)
from racecoach.clokkr import ClokkrEventIds

class ClokkrTests(unittest.TestCase):
    def test_discovers_event_identifiers(self):
        event_id = "11111111-1111-1111-1111-111111111111"
        series_id = "22222222-2222-2222-2222-222222222222"
        course_id = "33333333-3333-3333-3333-333333333333"

        page = (
            rf'\"event\":{{\"id\":\"{event_id}\"}}'
            rf'\"seriesId\":\"{series_id}\"'
            rf'\"course\":{{\"id\":\"{course_id}\"}}'
        )

        discovered = discover_event_ids(page)

        self.assertEqual(discovered.event_id, event_id)
        self.assertEqual(discovered.series_id, series_id)
        self.assertEqual(discovered.course_id, course_id)

    def test_classifies_clean_run(self):
        status = classify_clokkr_run(
            {
                "time": "37.130",
                "coneCount": 0,
                "stationConeCount": [],
                "dnf": False,
                "hadRerun": False,
            }
        )

        self.assertEqual(status, "clean")

    def test_classifies_cone_run(self):
        status = classify_clokkr_run(
            {
                "time": "36.900",
                "coneCount": 1,
                "stationConeCount": [],
                "dnf": False,
                "hadRerun": False,
            }
        )

        self.assertEqual(status, "cone")

    def test_classifies_dnf_run(self):
        status = classify_clokkr_run(
            {
                "time": "36.927",
                "coneCount": 0,
                "stationConeCount": [],
                "dnf": True,
                "hadRerun": False,
            }
        )

        self.assertEqual(status, "dnf")

    def test_rerun_fails_closed(self):
        status = classify_clokkr_run(
            {
                "time": "37.000",
                "coneCount": 0,
                "stationConeCount": [],
                "dnf": False,
                "hadRerun": True,
            }
        )

        self.assertEqual(status, "unknown")

    def test_parser_returns_only_configured_car(self):
        course_id = "33333333-3333-3333-3333-333333333333"

        document = {
            "json": {
                "data": {
                    "drivers": [
                        {
                            "firstName": "Excluded",
                            "email": "excluded@example.invalid",
                            "phone": "555-0000",
                            "carNumber": 100,
                            "carClass": "OTHER",
                            "carName": "Other Car",
                            "Run": {course_id: []},
                        },
                        {
                            "firstName": "Target",
                            "email": "target@example.invalid",
                            "phone": "555-1111",
                            "carNumber": 353,
                            "carClass": "P-05",
                            "carName": "2013 Porsche Carrera S",
                            "Run": {
                                course_id: [
                                    {
                                        "index": 1,
                                        "time": "38.653",
                                        "adjustedTime": "38.653",
                                        "coneCount": 0,
                                        "stationConeCount": [],
                                        "dnf": False,
                                        "hadRerun": False,
                                        "isExtraRun": False,
                                    },
                                    {
                                        "index": 2,
                                        "time": "39.016",
                                        "adjustedTime": "40.016",
                                        "coneCount": 1,
                                        "stationConeCount": [],
                                        "dnf": False,
                                        "hadRerun": False,
                                        "isExtraRun": False,
                                    },
                                ]
                            },
                        },
                    ]
                }
            }
        }


    def test_builds_public_batch_request(self):
        from racecoach.clokkr import ClokkrEventIds

        request = build_results_request(
            "https://app.clokkr.com/results/test-event",
            ClokkrEventIds(
                event_id=(
                    "11111111-1111-1111-1111-111111111111"
                ),
                series_id=(
                    "22222222-2222-2222-2222-222222222222"
                ),
                course_id=(
                    "33333333-3333-3333-3333-333333333333"
                ),
            ),
        )

        self.assertIn(
            "/api/trpc/results.getAllByDriverTimeForEvent,",
            request.full_url,
        )
        self.assertIn("batch=1", request.full_url)
        self.assertNotIn("cookie", request.headers)
        self.assertEqual(
            request.headers["Referer"],
            "https://app.clokkr.com/results/test-event",
        )

    def test_fetches_only_configured_driver(self):
        event_id = "11111111-1111-1111-1111-111111111111"
        series_id = "22222222-2222-2222-2222-222222222222"
        course_id = "33333333-3333-3333-3333-333333333333"

        page = (
            rf'\"event\":{{\"id\":\"{event_id}\"}}'
            rf'\"seriesId\":\"{series_id}\"'
            rf'\"course\":{{\"id\":\"{course_id}\"}}'
        ).encode("utf-8")

        document = {
            "json": {
                "data": {
                    "drivers": [
                        {
                            "firstName": "Target",
                            "email": "private@example.invalid",
                            "phone": "555-1111",
                            "carNumber": 353,
                            "carClass": "P-05",
                            "carName": "2013 Porsche Carrera S",
                            "Run": {
                                course_id: [
                                    {
                                        "index": 1,
                                        "time": "37.130",
                                        "adjustedTime": "37.130",
                                        "coneCount": 0,
                                        "stationConeCount": [],
                                        "dnf": False,
                                        "hadRerun": False,
                                        "isExtraRun": False,
                                    }
                                ]
                            },
                        }
                    ]
                }
            }
        }

        results = (
            json.dumps(document) + "\n"
        ).encode("utf-8")

        class FakeResponse:
            def __init__(self, body):
                self.body = body

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return self.body

            def __iter__(self):
                return iter(
                    self.body.splitlines(keepends=True)
                )

        with patch(
            "racecoach.clokkr.urllib.request.urlopen",
            side_effect=[
                FakeResponse(page),
                FakeResponse(results),
            ],
        ) as urlopen:
            result = fetch_driver_result(
                "https://app.clokkr.com/results/test-event",
                "353",
            )

        self.assertEqual(urlopen.call_count, 2)
        self.assertEqual(result.car_number, "353")
        self.assertEqual(len(result.runs), 1)
        self.assertEqual(result.runs[0].status, "clean")
        self.assertFalse(hasattr(result, "email"))
        self.assertFalse(hasattr(result, "phone"))



if __name__ == "__main__":
    unittest.main()
