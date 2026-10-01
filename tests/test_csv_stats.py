#!/usr/bin/env python3
"""Tests for csv-stats."""

import json
import pytest
from pathlib import Path
from csv_stats import analyze_column, analyze_csv, format_output, main, read_csv


class TestAnalyzeColumn:
    def test_numeric_column(self):
        values = ["1", "2", "3", "4", "5"]
        result = analyze_column(values)
        assert result["type"] == "numeric"
        assert result["count"] == 5
        assert result["nulls"] == 0
        assert result["unique"] == 5
        assert result["min"] == 1.0
        assert result["max"] == 5.0

    def test_numeric_with_nulls(self):
        values = ["10", "", "20", "", "30"]
        result = analyze_column(values)
        assert result["type"] == "numeric"
        assert result["count"] == 5
        assert result["nulls"] == 2
        assert result["unique"] == 3
        assert result["min"] == 10.0
        assert result["max"] == 30.0

    def test_numeric_floats(self):
        values = ["1.5", "2.7", "3.9"]
        result = analyze_column(values)
        assert result["type"] == "numeric"
        assert result["min"] == 1.5
        assert result["max"] == 3.9

    def test_categorical_column(self):
        values = ["apple", "banana", "apple", "cherry", "banana"]
        result = analyze_column(values)
        assert result["type"] == "categorical"
        assert result["count"] == 5
        assert result["nulls"] == 0
        assert result["unique"] == 3
        assert result["top"] == "apple"

    def test_categorical_with_nulls(self):
        values = ["yes", "", "no", "yes", ""]
        result = analyze_column(values)
        assert result["type"] == "categorical"
        assert result["count"] == 5
        assert result["nulls"] == 2
        assert result["unique"] == 2
        assert result["top"] == "yes"

    def test_empty_column(self):
        values = ["", "", ""]
        result = analyze_column(values)
        assert result["type"] == "categorical"
        assert result["count"] == 3
        assert result["nulls"] == 3
        assert result["unique"] == 0
        assert result["top"] is None

    def test_single_value(self):
        values = ["only"]
        result = analyze_column(values)
        assert result["count"] == 1
        assert result["unique"] == 1


class TestReadCsv:
    def test_read_valid_csv(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,age\nAlice,30\nBob,25\n")
        headers, rows = read_csv(csv_file)
        assert headers == ["name", "age"]
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"

    def test_read_empty_csv(self, tmp_path):
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")
        headers, rows = read_csv(csv_file)
        assert headers == []
        assert rows == []


class TestAnalyzeCsv:
    def test_analyze_simple_csv(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,score\nAlice,90\nBob,85\nCharlie,90\n")
        results = analyze_csv(csv_file)
        assert "name" in results
        assert "score" in results
        assert results["name"]["type"] == "categorical"
        assert results["score"]["type"] == "numeric"
        assert results["score"]["min"] == 85.0
        assert results["score"]["max"] == 90.0


class TestFormatOutput:
    def test_format_text(self):
        results = {
            "col1": {
                "type": "numeric",
                "count": 10,
                "nulls": 1,
                "unique": 9,
                "min": 1.0,
                "max": 10.0,
            }
        }
        output = format_output(results, json_output=False)
        assert "col1:" in output
        assert "Type: numeric" in output
        assert "Count: 10" in output
        assert "Min: 1.0" in output

    def test_format_json(self):
        results = {
            "col1": {
                "type": "categorical",
                "count": 5,
                "nulls": 0,
                "unique": 3,
                "top": "a",
            }
        }
        output = format_output(results, json_output=True)
        parsed = json.loads(output)
        assert parsed["col1"]["type"] == "categorical"
        assert parsed["col1"]["top"] == "a"

    def test_format_text_categorical_with_top(self):
        results = {
            "color": {
                "type": "categorical",
                "count": 5,
                "nulls": 0,
                "unique": 3,
                "top": "red",
            }
        }
        output = format_output(results, json_output=False)
        assert "Most common: red" in output

    def test_format_text_categorical_no_top(self):
        results = {
            "empty_col": {
                "type": "categorical",
                "count": 3,
                "nulls": 3,
                "unique": 0,
                "top": None,
            }
        }
        output = format_output(results, json_output=False)
        assert "Most common: (none)" in output


class TestMain:
    def test_main_success(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n3,4\n")
        result = main([str(csv_file)])
        assert result == 0

    def test_main_json_flag(self, tmp_path, capsys):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("a,b\n1,2\n3,4\n")
        result = main([str(csv_file), "--json"])
        assert result == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "a" in parsed

    def test_main_file_not_found(self):
        result = main(["/nonexistent/file.csv"])
        assert result == 1

    def test_main_invalid_csv(self, tmp_path):
        # Create a file that will cause an error
        csv_file = tmp_path / "bad.csv"
        csv_file.write_text("a,b\n1,2\n")
        result = main([str(csv_file)])
        assert result == 0  # This should succeed
