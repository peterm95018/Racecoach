from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Iterable



UUID_PATTERN = (
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12})"
)

TRPC_PROCEDURES = (
    "results.getAllByDriverTimeForEvent",
    "results.getAllByDriverPaxForEvent",
    "results.getAllByClassForEvent",
    "results.getAllByDriverGroup",
    "run.getLastFew",
    "queue.getForResults",
)

@dataclass(frozen=True)
class ClokkrEventIds:
    event_id: str
    series_id: str
    course_id: str


@dataclass(frozen=True)
class ClokkrRun:
    index: int
    time_s: float | None
    adjusted_time_s: float | None
    cone_count: int
    status: str
    had_rerun: bool
    is_extra_run: bool


@dataclass(frozen=True)
class ClokkrDriverResult:
    car_number: str
    car_class: str
    car_name: str
    runs: tuple[ClokkrRun, ...]


def discover_event_ids(page: str) -> ClokkrEventIds:
    patterns = {
        "event_id": (
            rf'\\?"event\\?"\s*:\s*\{{'
            rf'.{{0,300}}?\\?"id\\?"\s*:\s*\\?"'
            rf"{UUID_PATTERN}"
        ),
        "series_id": (
            rf'\\?"seriesId\\?"\s*:\s*\\?"'
            rf"{UUID_PATTERN}"
        ),
        "course_id": (
            rf'\\?"course\\?"\s*:\s*\{{'
            rf'.{{0,300}}?\\?"id\\?"\s*:\s*\\?"'
            rf"{UUID_PATTERN}"
        ),
    }

    discovered = {}

    for label, pattern in patterns.items():
        match = re.search(
            pattern,
            page,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if match is None:
            raise ValueError(
                f"Clokkr {label} was not found in results page"
            )

        discovered[label] = match.group(1)

    return ClokkrEventIds(**discovered)


def classify_clokkr_run(run: dict) -> str:
    station_cones = run.get("stationConeCount") or []

    station_dnf = any(
        isinstance(station, dict)
        and station.get("dnf") is True
        for station in station_cones
    )

    if run.get("dnf") is True or station_dnf:
        return "dnf"

    cone_value = run.get("coneCount")

    try:
        cone_count = int(cone_value)
    except (TypeError, ValueError):
        return "unknown"

    if cone_count > 0:
        return "cone"

    if run.get("hadRerun") is True:
        return "unknown"

    if run.get("time") is None:
        return "unknown"

    return "clean"


def optional_float(value: object) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def sanitize_driver(
    driver: dict,
    course_id: str,
) -> ClokkrDriverResult:
    run_mapping = driver.get("Run") or {}

    if not isinstance(run_mapping, dict):
        raise ValueError("Invalid Clokkr Run mapping")

    raw_runs = run_mapping.get(course_id) or []

    if not isinstance(raw_runs, list):
        raise ValueError("Invalid Clokkr course runs")

    runs = []

    for raw_run in raw_runs:
        if not isinstance(raw_run, dict):
            continue

        try:
            index = int(raw_run.get("index"))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Clokkr run is missing a valid index"
            ) from exc

        try:
            cone_count = int(raw_run.get("coneCount", 0))
        except (TypeError, ValueError):
            cone_count = 0

        runs.append(
            ClokkrRun(
                index=index,
                time_s=optional_float(raw_run.get("time")),
                adjusted_time_s=optional_float(
                    raw_run.get("adjustedTime")
                ),
                cone_count=cone_count,
                status=classify_clokkr_run(raw_run),
                had_rerun=raw_run.get("hadRerun") is True,
                is_extra_run=raw_run.get("isExtraRun") is True,
            )
        )

    return ClokkrDriverResult(
        car_number=str(driver.get("carNumber", "")).strip(),
        car_class=str(driver.get("carClass", "")).strip(),
        car_name=str(driver.get("carName", "")).strip(),
        runs=tuple(sorted(runs, key=lambda run: run.index)),
    )


def find_driver_result(
    value: object,
    car_number: str,
    course_id: str,
) -> ClokkrDriverResult | None:
    if isinstance(value, dict):
        drivers = value.get("drivers")

        if isinstance(drivers, list):
            for driver in drivers:
                if (
                    isinstance(driver, dict)
                    and str(driver.get("carNumber", "")).strip()
                    == str(car_number).strip()
                ):
                    return sanitize_driver(driver, course_id)

        for nested in value.values():
            result = find_driver_result(
                nested,
                car_number,
                course_id,
            )

            if result is not None:
                return result

    elif isinstance(value, list):
        for nested in value:
            result = find_driver_result(
                nested,
                car_number,
                course_id,
            )

            if result is not None:
                return result

    return None


def parse_results_jsonl(
    lines: Iterable[str | bytes],
    car_number: str,
    course_id: str,
) -> ClokkrDriverResult:
    for line in lines:
        if isinstance(line, bytes):
            line = line.decode("utf-8")

        if not line.strip():
            continue

        document = json.loads(line)
        result = find_driver_result(
            document,
            car_number,
            course_id,
        )

        if result is not None:
            return result

    raise ValueError(
        f"Car number {car_number} was not found in Clokkr results"
    )

def fetch_results_page(
    results_url: str,
    *,
    timeout: int = 20,
) -> str:
    request = urllib.request.Request(
        results_url,
        headers={
            "Accept": "text/html",
            "User-Agent": "RaceCoach/0.1",
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        return response.read().decode(
            "utf-8",
            errors="replace",
        )


def build_results_request(
    results_url: str,
    event_ids: ClokkrEventIds,
) -> urllib.request.Request:
    parsed_url = urllib.parse.urlsplit(results_url)

    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError(
            "Clokkr results URL must be an absolute HTTPS URL"
        )

    procedures = ",".join(TRPC_PROCEDURES)
    endpoint = (
        f"{parsed_url.scheme}://{parsed_url.netloc}"
        f"/api/trpc/{procedures}"
    )

    payload = {
        "0": {
            "json": {
                "eventId": event_ids.event_id,
            }
        },
        "1": {
            "json": {
                "eventId": event_ids.event_id,
            }
        },
        "2": {
            "json": {
                "eventId": event_ids.event_id,
                "seriesId": event_ids.series_id,
            }
        },
        "3": {
            "json": {
                "eventId": event_ids.event_id,
            }
        },
        "4": {
            "json": {
                "eventId": event_ids.event_id,
                "take": 5,
                "courseId": None,
                "isRunTicker": True,
            },
            "meta": {
                "values": {
                    "courseId": ["undefined"],
                }
            },
        },
        "5": {
            "json": {
                "eventId": event_ids.event_id,
            }
        },
    }

    query = urllib.parse.urlencode(
        {
            "batch": "1",
            "input": json.dumps(
                payload,
                separators=(",", ":"),
            ),
        }
    )

    return urllib.request.Request(
        f"{endpoint}?{query}",
        headers={
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Referer": results_url,
            "trpc-accept": "application/jsonl",
            "User-Agent": "RaceCoach/0.1",
            "x-trpc-source": "nextjs-react",
        },
    )


def fetch_driver_result(
    results_url: str,
    car_number: str,
    *,
    timeout: int = 20,
) -> ClokkrDriverResult:
    page = fetch_results_page(
        results_url,
        timeout=timeout,
    )
    event_ids = discover_event_ids(page)
    request = build_results_request(
        results_url,
        event_ids,
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        return parse_results_jsonl(
            response,
            car_number,
            event_ids.course_id,
        )