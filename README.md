# csv-stats

Quick CSV file analyzer - get column statistics without opening Excel or writing pandas code.

## Features

- **Automatic type detection**: Identifies numeric vs categorical columns
- **Quick stats**: Count, nulls, unique values, min/max for numbers, most common for text
- **JSON output**: Use `--json` for programmatic access
- **Fast**: No dependencies, pure Python

## Installation

```bash
# With uv
uv tool install csv-stats

# Or pip
pip install csv-stats
```

## Usage

```bash
# Analyze a CSV file
csv-stats data.csv

# Output as JSON
csv-stats data.csv --json

# Run as module
python -m csv_stats data.csv
```

## Example Output

```
name:
  Type: categorical
  Count: 100
  Nulls: 2
  Unique: 47
  Most common: Alice

age:
  Type: numeric
  Count: 100
  Nulls: 2
  Unique: 35
  Min: 18.0
  Max: 92.0
```

## Development

```bash
# Create venv
uv venv

# Install with dev deps
uv pip install -e ".[dev]"

# Run tests
pytest

# Check coverage
pytest --cov=csv_stats --cov-report=term-missing
```

## License

MIT
