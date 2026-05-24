"""
scripts/import_colleges.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CSV Import System for Engineering College Selection Platform

Supported sources: NIRF, AICTE, JOSAA, AP_EAMCET, TS_EAMCET, MANUAL

Usage (from project root):
  python scripts/import_colleges.py --file data/sample_csvs/nirf_2024.csv --source NIRF

CSV Column Reference (see data/sample_csvs/ for templates):
  Required: name, state
  Optional: See COLUMN_MAP below
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime

# Add parent directory to path so we can import Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import (
    College, State, City, Branch, Facility, Course, ImportLog
)


# ─── COLUMN MAPPING ────────────────────────────────────────────
# Maps CSV column names → College model attributes
# Keys are what we look for in the CSV (case-insensitive)
COLUMN_MAP = {
    # Identity
    "name":                    "name",
    "college_name":            "name",
    "institution_name":        "name",
    "short_name":              "short_name",
    "college_type":            "college_type",
    "type":                    "college_type",
    "establishment_year":      "establishment_year",
    "year_established":        "establishment_year",
    "aicte_id":                "aicte_id",
    "aicte_approval_id":       "aicte_id",
    "nirf_id":                 "nirf_id",

    # Location
    "address":                 "address",
    "city":                    "_city",          # special: lookup/create City
    "state":                   "_state",         # special: lookup/create State
    "pincode":                 "pincode",

    # Contact
    "website":                 "official_website",
    "official_website":        "official_website",
    "email":                   "email",
    "phone":                   "phone",

    # Rankings
    "nirf_rank":               "nirf_rank",
    "rank":                    "nirf_rank",
    "nirf_score":              "nirf_score",
    "nirf_year":               "nirf_year",
    "state_rank":              "state_rank",
    "naac_grade":              "naac_grade",

    # Fees
    "annual_fees":             "annual_fees_min",
    "annual_fees_min":         "annual_fees_min",
    "fees":                    "annual_fees_min",
    "annual_fees_max":         "annual_fees_max",

    # Placements
    "placement_percentage":    "placement_percentage",
    "placement_percent":       "placement_percentage",
    "placement_%":             "placement_percentage",
    "avg_package_lpa":         "avg_package_lpa",
    "average_package":         "avg_package_lpa",
    "highest_package_lpa":     "highest_package_lpa",
    "highest_package":         "highest_package_lpa",
    "top_recruiters":          "top_recruiters",

    # Hostel
    "hostel_available":        "hostel_available",
    "hostel":                  "hostel_available",
    "boys_hostel":             "boys_hostel",
    "girls_hostel":            "girls_hostel",

    # Others
    "affiliated_university":   "affiliated_university",
    "university":              "affiliated_university",
    "autonomous":              "autonomous",
    "description":             "description",
    "total_seats":             "total_seats",
    "branches":                "_branches",      # special: comma-separated list
    "facilities":              "_facilities",    # special: comma-separated list
}

# ─── BOOLEAN PARSER ────────────────────────────────────────────

def parse_bool(value):
    """Convert various representations to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in ("yes", "true", "1", "y", "available")
    return False


# ─── STATE / CITY HELPERS ──────────────────────────────────────

_state_cache = {}
_city_cache  = {}
_branch_cache = {}
_facility_cache = {}


def get_or_create_state(name: str):
    """Get existing state or create new one."""
    name = name.strip().title()
    if name in _state_cache:
        return _state_cache[name]
    state = State.query.filter_by(name=name).first()
    if not state:
        state = State(name=name)
        db.session.add(state)
        db.session.flush()  # Get ID without full commit
    _state_cache[name] = state
    return state


def get_or_create_city(name: str, state_id: int):
    """Get existing city or create new one."""
    key = f"{name}_{state_id}"
    if key in _city_cache:
        return _city_cache[key]
    city = City.query.filter_by(name=name.strip().title(), state_id=state_id).first()
    if not city:
        city = City(name=name.strip().title(), state_id=state_id)
        db.session.add(city)
        db.session.flush()
    _city_cache[key] = city
    return city


def get_or_create_branch(name: str):
    """Get existing branch or create new one."""
    name = name.strip()
    if name in _branch_cache:
        return _branch_cache[name]
    branch = Branch.query.filter_by(name=name).first()
    if not branch:
        branch = Branch(name=name)
        db.session.add(branch)
        db.session.flush()
    _branch_cache[name] = branch
    return branch


def get_or_create_facility(name: str):
    """Get existing facility or create new one."""
    name = name.strip()
    if name in _facility_cache:
        return _facility_cache[name]
    facility = Facility.query.filter_by(name=name).first()
    if not facility:
        facility = Facility(name=name)
        db.session.add(facility)
        db.session.flush()
    _facility_cache[name] = facility
    return facility


# ─── MAIN IMPORT FUNCTION ──────────────────────────────────────

def import_csv(filepath: str, source: str = "MANUAL", mode: str = "upsert", log_id: int = None) -> dict:
    """
    Parse and import college CSV into the database.

    Args:
        filepath: Absolute or relative path to CSV file
        source: Data source tag (NIRF, AICTE, etc.)
        mode: "upsert" (insert+update) or "insert_only"
        log_id: ImportLog ID for status tracking

    Returns:
        dict with keys: total, added, updated, failed
    """
    result = {"total": 0, "added": 0, "updated": 0, "failed": 0, "errors": []}

    # ── Read CSV ─────────────────────────────────────────────
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig", dtype=str)
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding="latin-1", dtype=str)

    # Normalize column names: lowercase, strip whitespace
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    df = df.where(pd.notnull(df), None)  # Replace NaN with None

    result["total"] = len(df)
    print(f"[IMPORT] Reading {result['total']} rows from {filepath}")
    print(f"[IMPORT] Columns found: {list(df.columns)}")

    # ── Process each row ─────────────────────────────────────
    for idx, row in df.iterrows():
        try:
            _process_row(row, source=source, mode=mode, result=result)

            # Commit every 50 rows to avoid huge transactions
            if (idx + 1) % 50 == 0:
                db.session.commit()
                print(f"[IMPORT] Processed {idx + 1}/{result['total']} rows...")

        except Exception as e:
            result["failed"] += 1
            error_msg = f"Row {idx + 2}: {str(e)}"
            result["errors"].append(error_msg)
            print(f"[ERROR] {error_msg}")
            db.session.rollback()

    # Final commit
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    print(f"[IMPORT] Done! Added: {result['added']}, Updated: {result['updated']}, Failed: {result['failed']}")
    return result


def _process_row(row, source: str, mode: str, result: dict):
    """Process a single CSV row into the database."""

    # Build a normalized dict from the row using COLUMN_MAP
    mapped = {}
    for csv_col, model_attr in COLUMN_MAP.items():
        if csv_col in row.index and row[csv_col] is not None:
            val = row[csv_col]
            if isinstance(val, str):
                val = val.strip()
            if val == "" or val == "NA" or val == "N/A":
                val = None
            if val is not None:
                mapped[model_attr] = val

    # ── Validate required field ───────────────────────────
    college_name = mapped.get("name")
    if not college_name or len(college_name) < 3:
        raise ValueError("Missing or invalid college name")

    # ── Handle State (required) ───────────────────────────
    state_name = mapped.pop("_state", None)
    if not state_name:
        raise ValueError("Missing state")
    state = get_or_create_state(state_name)

    # ── Handle City (optional) ────────────────────────────
    city_name = mapped.pop("_city", None)
    city_id = None
    if city_name:
        city = get_or_create_city(city_name, state.id)
        city_id = city.id

    # ── Handle Branches ───────────────────────────────────
    branches_raw = mapped.pop("_branches", None)
    branch_objs = []
    if branches_raw:
        for bname in branches_raw.split(","):
            bname = bname.strip()
            if bname:
                branch_objs.append(get_or_create_branch(bname))

    # ── Handle Facilities ─────────────────────────────────
    facilities_raw = mapped.pop("_facilities", None)
    facility_objs = []
    if facilities_raw:
        for fname in facilities_raw.split(","):
            fname = fname.strip()
            if fname:
                facility_objs.append(get_or_create_facility(fname))

    # ── Cast types ────────────────────────────────────────
    int_fields = ["nirf_rank", "state_rank", "establishment_year", "annual_fees_min",
                  "annual_fees_max", "total_seats", "intake_capacity"]
    float_fields = ["nirf_score", "placement_percentage", "avg_package_lpa", "highest_package_lpa"]
    bool_fields = ["hostel_available", "boys_hostel", "girls_hostel", "autonomous"]

    for field in int_fields:
        if field in mapped and mapped[field] is not None:
            try:
                mapped[field] = int(float(str(mapped[field]).replace(",", "").replace("₹", "")))
            except (ValueError, TypeError):
                mapped[field] = None

    for field in float_fields:
        if field in mapped and mapped[field] is not None:
            try:
                mapped[field] = float(str(mapped[field]).replace(",", "").replace("%", ""))
            except (ValueError, TypeError):
                mapped[field] = None

    for field in bool_fields:
        if field in mapped and mapped[field] is not None:
            mapped[field] = parse_bool(mapped[field])

    # ── Clamp placement % ─────────────────────────────────
    if mapped.get("placement_percentage") is not None:
        mapped["placement_percentage"] = min(100.0, max(0.0, mapped["placement_percentage"]))

    # ── Find existing college (by name + state) ───────────
    existing = College.query.filter_by(name=college_name, state_id=state.id).first()

    if existing:
        if mode == "insert_only":
            return  # Skip if exists
        # Update mode
        for key, val in mapped.items():
            if key not in ("name",) and val is not None:
                setattr(existing, key, val)
        existing.state_id = state.id
        existing.city_id = city_id
        existing.data_source = source
        existing.last_updated = datetime.utcnow()
        if branch_objs:
            existing.branches = branch_objs
        if facility_objs:
            existing.facilities = facility_objs
        result["updated"] += 1
    else:
        # Create new college
        college = College(
            state_id=state.id,
            city_id=city_id,
            data_source=source,
            **{k: v for k, v in mapped.items() if hasattr(College, k)},
        )
        college.branches = branch_objs
        college.facilities = facility_objs
        db.session.add(college)
        result["added"] += 1

    db.session.flush()


# ─── CLI ENTRY POINT ───────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import college CSV into database")
    parser.add_argument("--file", required=True, help="Path to CSV file")
    parser.add_argument("--source", default="MANUAL", choices=[
        "NIRF", "AICTE", "JOSAA", "AP_EAMCET", "TS_EAMCET", "MANUAL"
    ])
    parser.add_argument("--mode", default="upsert", choices=["upsert", "insert_only"])
    parser.add_argument("--env", default="development")
    args = parser.parse_args()

    app = create_app(args.env)
    with app.app_context():
        result = import_csv(args.file, source=args.source, mode=args.mode)
        print(f"\n✅ Import complete: {result}")
