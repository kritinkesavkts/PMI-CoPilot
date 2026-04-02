"""
Tests for parser service — validates file parsing across supported types.
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.parser_service import parser_service
from app.schemas.documents import FileType


class TestTxtParser:
    def test_parse_basic_txt(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("AcquireCo uses Salesforce.\nTargetCo uses HubSpot.")
            f.flush()

            result = parser_service.parse(f.name, "doc1", "test.txt", FileType.TXT)

            assert result.document_id == "doc1"
            assert result.filename == "test.txt"
            assert result.file_type == FileType.TXT
            assert "AcquireCo" in result.raw_text
            assert "HubSpot" in result.raw_text
            assert len(result.sections) == 1

            os.unlink(f.name)

    def test_parse_empty_txt(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            f.flush()

            result = parser_service.parse(f.name, "doc2", "empty.txt", FileType.TXT)
            assert result.raw_text == ""

            os.unlink(f.name)


class TestCsvParser:
    def test_parse_basic_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Company,System,Cost\n")
            f.write("AcquireCo,Salesforce,800000\n")
            f.write("TargetCo,HubSpot,120000\n")
            f.flush()

            result = parser_service.parse(f.name, "doc3", "systems.csv", FileType.CSV)

            assert result.file_type == FileType.CSV
            assert result.row_count == 2
            assert result.column_names == ["Company", "System", "Cost"]
            assert "AcquireCo" in result.raw_text

            os.unlink(f.name)

    def test_csv_metadata(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Name,Role,Department\n")
            f.write("Alice,VP Sales,Sales\n")
            f.write("Bob,CFO,Finance\n")
            f.write("Carol,CTO,Engineering\n")
            f.flush()

            result = parser_service.parse(f.name, "doc4", "people.csv", FileType.CSV)

            assert result.row_count == 3
            assert "Department" in result.column_names

            os.unlink(f.name)


class TestParserRouting:
    def test_unsupported_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            parser_service.parse("/fake/path", "x", "file.xyz", "xyz")

    def test_routes_to_correct_parser(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            f.flush()

            result = parser_service.parse(f.name, "r1", "file.txt", FileType.TXT)
            assert result.file_type == FileType.TXT

            os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
