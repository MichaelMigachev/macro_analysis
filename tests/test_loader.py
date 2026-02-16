"""Tests for the DataLoader module."""
import pytest
import csv
from pathlib import Path
from unittest.mock import mock_open, patch

from macro_analysis.loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class."""

    @pytest.fixture
    def sample_csv_content(self):
        """Fixture providing sample CSV content."""
        return """country,year,gdp,gdp_growth,inflation,unemployment,population,continent
United States,2023,25462,2.1,3.4,3.7,339,North America
United States,2022,23315,2.1,8.0,3.6,338,North America
China,2023,17963,5.2,2.5,5.2,1425,Asia
China,2022,17734,3.0,2.0,5.6,1423,Asia
Germany,2023,4086,-0.3,6.2,3.0,83,Europe"""

    @pytest.fixture
    def sample_csv_content_with_headers_only(self):
        """Fixture with only headers, no data."""
        return """country,year,gdp,gdp_growth,inflation,unemployment,population,continent\n"""

    @pytest.fixture
    def temp_csv_files(self, tmp_path, sample_csv_content):
        """Create temporary CSV files for testing."""
        # Create first file
        file1 = tmp_path / "data1.csv"
        file1.write_text(sample_csv_content, encoding='utf-8')

        # Create second file with additional data
        file2 = tmp_path / "data2.csv"
        file2.write_text("""country,year,gdp,gdp_growth,inflation,unemployment,population,continent
France,2023,3049,0.9,5.2,7.1,68,Europe
Japan,2023,4231,1.2,2.8,2.6,125,Asia""", encoding='utf-8')

        return [str(file1), str(file2)]

    def test_load_single_file(self, tmp_path, sample_csv_content):
        """Test loading data from a single CSV file."""
        # Create test file
        test_file = tmp_path / "test.csv"
        test_file.write_text(sample_csv_content, encoding='utf-8')

        loader = DataLoader()
        result = loader.load_files([str(test_file)])

        # Check results
        assert len(result) == 5
        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)

        # Check first row
        assert result[0]['country'] == 'United States'
        assert result[0]['year'] == '2023'
        assert result[0]['gdp'] == '25462'
        assert result[0]['continent'] == 'North America'

    def test_load_multiple_files(self, temp_csv_files):
        """Test loading data from multiple CSV files."""
        loader = DataLoader()
        result = loader.load_files(temp_csv_files)

        # Should have 5 + 2 = 7 rows
        assert len(result) == 7

        # Check that data from both files is present
        countries = {row['country'] for row in result}
        assert 'United States' in countries
        assert 'China' in countries
        assert 'Germany' in countries
        assert 'France' in countries
        assert 'Japan' in countries

    def test_load_empty_file(self, tmp_path):
        """Test loading an empty CSV file."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("", encoding='utf-8')

        loader = DataLoader()
        result = loader.load_files([str(empty_file)])

        # Empty file with no headers should return empty list
        assert result == []

    def test_load_file_with_headers_only(self, tmp_path, sample_csv_content_with_headers_only):
        """Test loading a CSV file that has headers but no data."""
        test_file = tmp_path / "headers_only.csv"
        test_file.write_text(sample_csv_content_with_headers_only, encoding='utf-8')

        loader = DataLoader()
        result = loader.load_files([str(test_file)])

        # Should return empty list (headers but no data rows)
        assert result == []

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        loader = DataLoader()

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_files(["nonexistent.csv"])

        assert "Файл не найден" in str(exc_info.value)
        assert "nonexistent.csv" in str(exc_info.value)

    def test_load_files_with_mixed_existence(self, tmp_path):
        """Test loading mix of existing and non-existing files."""
        # Create one valid file
        valid_file = tmp_path / "valid.csv"
        valid_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        loader = DataLoader()

        # Should raise FileNotFoundError on the first missing file
        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_files([str(valid_file), "nonexistent.csv"])

        assert "Файл не найден" in str(exc_info.value)

    def test_load_file_with_different_encodings(self, tmp_path):
        """Test loading files with different encodings."""
        # Test with UTF-8
        utf8_file = tmp_path / "utf8.csv"
        utf8_file.write_text("country,gdp\nFrançe,100\n", encoding='utf-8')

        loader = DataLoader()
        result = loader.load_files([str(utf8_file)])

        assert len(result) == 1
        assert result[0]['country'] == 'Françe'

    def test_load_file_with_different_delimiters(self, tmp_path):
        """Test that csv.DictReader handles different delimiters correctly."""
        # csv.DictReader defaults to comma, so we're testing that it works with commas
        test_file = tmp_path / "test.csv"
        test_file.write_text("country;gdp\nUSA;100\n", encoding='utf-8')  # Semicolon delimiter

        loader = DataLoader()
        result = loader.load_files([str(test_file)])

        # Should treat the whole line as one field because of wrong delimiter
        assert len(result) == 1
        assert 'country;gdp' in result[0]  # Headers will be treated as data

    def test_load_file_with_extra_spaces(self, tmp_path):
        """Test loading CSV with extra spaces in values."""
        test_file = tmp_path / "spaces.csv"
        test_file.write_text("country, gdp\nUSA, 100\n Germany, 200\n", encoding='utf-8')

        loader = DataLoader()
        result = loader.load_files([str(test_file)])

        # Spaces should be preserved as they are part of the values
        assert len(result) == 2
        assert result[0]['country'] == 'USA'
        assert result[0][' gdp'] == ' 100'  # Note the space in key and value
        assert result[1]['country'] == ' Germany'  # Leading space preserved

    def test_load_file_with_quoted_values(self, tmp_path):
        """Test loading CSV with quoted values."""
        test_file = tmp_path / "quoted.csv"
        test_file.write_text('country,gdp\n"United States","100"\n"Germany, EU","200"\n', encoding='utf-8')

        loader = DataLoader()
        result = loader.load_files([str(test_file)])

        assert len(result) == 2
        assert result[0]['country'] == 'United States'
        assert result[0]['gdp'] == '100'
        assert result[1]['country'] == 'Germany, EU'  # Comma inside quotes preserved
        assert result[1]['gdp'] == '200'

    def test_load_file_with_malformed_csv(self, tmp_path):
        """Test handling of malformed CSV (uneven columns)."""
        test_file = tmp_path / "malformed.csv"
        test_file.write_text("country,gdp\nUSA,100,extra\nGermany,200\n", encoding='utf-8')

        loader = DataLoader()

        # csv.DictReader will handle malformed rows by putting extra data in a single field
        # This shouldn't raise an exception
        result = loader.load_files([str(test_file)])

        # First row has 3 fields, so the last one might be in a field with key None or extra
        assert len(result) == 2

    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_load_file_with_permission_error(self, mock_open):
        """Test handling of permission errors."""
        loader = DataLoader()

        with pytest.raises(Exception) as exc_info:
            loader.load_files(["test.csv"])

        assert "Ошибка чтения файла" in str(exc_info.value)
        assert "Permission denied" in str(exc_info.value)

    def test_load_very_large_file(self, tmp_path):
        """Test that loader can handle larger files (memory test)."""
        # Create a file with 1000 rows
        large_file = tmp_path / "large.csv"
        with open(large_file, 'w', encoding='utf-8') as f:
            f.write("country,year,gdp\n")
            for i in range(1000):
                f.write(f"Country{i},2023,{i * 100}\n")

        loader = DataLoader()
        result = loader.load_files([str(large_file)])

        assert len(result) == 1000

    def test_load_files_returns_list_of_dicts(self, temp_csv_files):
        """Test that returned data structure is correct."""
        loader = DataLoader()
        result = loader.load_files(temp_csv_files[:1])  # Use first file only

        assert isinstance(result, list)
        assert all(isinstance(row, dict) for row in result)

        # Check that all rows have the same keys (from headers)
        if result:
            first_row_keys = set(result[0].keys())
            for row in result[1:]:
                assert set(row.keys()) == first_row_keys

    def test_loader_does_not_modify_input_list(self, tmp_path):
        """Test that load_files doesn't modify the input file list."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        file_paths = [str(test_file)]
        file_paths_copy = file_paths.copy()

        loader = DataLoader()
        loader.load_files(file_paths)

        assert file_paths == file_paths_copy


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
