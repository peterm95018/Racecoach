# RaceCoach MVP

First iteration autocross telemetry coach.

## What it does

- Watches `uploads/` for RaceChrono CSV exports
- Moves processed files to `processed/`
- Compares each uploaded run against a reference CSV
- Produces Markdown coaching reports in `reports/`
- Focuses on over-slowing, coasting, braking force, throttle pickup, and segment time loss

## Install on Ubuntu

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip unzip

mkdir -p ~/racecoach
cd ~/racecoach
# unzip racecoach_mvp.zip here, then move contents from racecoach_mvp/ if needed

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## First test

```bash
source .venv/bin/activate
python -m racecoach.analyze_run uploads/YOUR_FILE.csv --event events/sample_event
```

## Watch mode

```bash
source .venv/bin/activate
python -m racecoach.watch_uploads --event events/sample_event
```

## iPhone / FTPManager workflow

Upload RaceChrono CSV files to:

```text
~/racecoach/uploads/
```

Retrieve reports from:

```text
~/racecoach/reports/
```

## Next setup step

Copy your fastest clean run to:

```text
events/sample_event/reference.csv
```

Then edit:

```text
events/sample_event/segments.yaml
```

Replace the sample distance ranges with actual course segment distances.
