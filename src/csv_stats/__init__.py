#!/usr/bin/env python3
"""CSV file analyzer - quick column statistics."""

import argparse
import csv
import sys
from pathlib import Path
from typing import Dict, List, Any


def analyze_column(values: List[str]) -> Dict[str, Any]:
    """Analyze a single column and return statistics."""
    total = len(values)
    nulls = sum(1 for v in values if v.strip() == "")
    
    # Try numeric analysis
    numeric_values = []
    for v in values:
        if v.strip() == "":
            continue
        try:
            numeric_values.append(float(v))
        except ValueError:
            pass
    
    # If all non-null values are numeric
    if len(numeric_values) == total - nulls and numeric_values:
        return {
            "type": "numeric",
            "count": total,
            "nulls": nulls,
            "min": min(numeric_values),
            "max": max(numeric_values),
            "unique": len(set(numeric_values)),
        }
    
    # Otherwise categorical
    non_null = [v for v in values if v.strip() != ""]
    return {
        "type": "categorical",
        "count": total,
        "nulls": nulls,
        "unique": len(set(non_null)),
        "top": max(set(non_null), key=non_null.count) if non_null else None,
    }


def read_csv(filepath: Path) -> tuple[List[str], List[Dict[str, str]]]:
    """Read CSV file and return headers and rows."""
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            return [], []
        headers = list(reader.fieldnames)
        rows = list(reader)
    return headers, rows


def analyze_csv(filepath: Path) -> Dict[str, Dict[str, Any]]:
    """Analyze all columns in a CSV file."""
    headers, rows = read_csv(filepath)
    
    results = {}
    for header in headers:
        values = [row.get(header, "") for row in rows]
        results[header] = analyze_column(values)
    
    return results


def format_output(results: Dict[str, Dict[str, Any]], json_output: bool = False) -> str:
    """Format analysis results for output."""
    if json_output:
        import json
        return json.dumps(results, indent=2)
    
    lines = []
    for col, stats in results.items():
        lines.append(f"\n{col}:")
        lines.append(f"  Type: {stats['type']}")
        lines.append(f"  Count: {stats['count']}")
        lines.append(f"  Nulls: {stats['nulls']}")
        lines.append(f"  Unique: {stats['unique']}")
        
        if stats['type'] == 'numeric':
            lines.append(f"  Min: {stats['min']}")
            lines.append(f"  Max: {stats['max']}")
        else:
            if stats['top']:
                lines.append(f"  Most common: {stats['top']}")
            else:
                lines.append("  Most common: (none)")

    return "\n".join(lines)


def main(argv: List[str] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Quick CSV file analyzer")
    parser.add_argument("file", type=Path, help="CSV file to analyze")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    results = analyze_csv(args.file)
    print(format_output(results, args.json))
    return 0