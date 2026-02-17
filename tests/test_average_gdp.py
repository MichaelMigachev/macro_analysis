"""Tests for the average GDP report."""
import pytest
from macro_analysis.reports.average_gdp import AverageGDPReport


class TestAverageGDPReport:
    """Test cases for AverageGDPReport class."""

    def test_generate_basic(self):
        """Test basic average GDP calculation."""
        data = [
            {'country': 'USA', 'gdp': '200'},
            {'country': 'USA', 'gdp': '300'},
            {'country': 'Germany', 'gdp': '250'}
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 2
        assert result[0]['Страна'] == 'USA'
        assert result[0]['Средний ВВП'] == 250.0
        assert result[1]['Страна'] == 'Germany'
        assert result[1]['Средний ВВП'] == 250.0

    def test_generate_with_floats(self):
        """Test with float values."""
        data = [
            {'country': 'USA', 'gdp': 200.5},
            {'country': 'USA', 'gdp': 300.7}
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 1
        assert result[0]['Средний ВВП'] == (200.5 + 300.7) / 2

    def test_generate_empty_data(self):
        """Test with empty data."""
        report = AverageGDPReport([])
        result = report.generate()
        assert result == []

    def test_generate_invalid_values(self):
        """Test handling of invalid values (should be skipped)."""
        data = [
            {'country': 'USA', 'gdp': '200'},
            {'country': 'USA', 'gdp': 'invalid'},
            {'country': 'USA', 'gdp': None},
            {'country': 'USA', 'gdp': ''},
            {'country': 'Germany', 'gdp': '250'},
            {'country': 'France', 'gdp': 123.45},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 3

        usa = next(r for r in result if r['Страна'] == 'USA')
        germany = next(r for r in result if r['Страна'] == 'Germany')
        france = next(r for r in result if r['Страна'] == 'France')

        assert usa['Средний ВВП'] == 200.0
        assert germany['Средний ВВП'] == 250.0
        assert france['Средний ВВП'] == 123.45

    def test_generate_missing_keys(self):
        """Test handling of missing keys (should be skipped)."""
        data = [
            {'country': 'USA', 'gdp': '200'},
            {'gdp': '300'},
            {'country': 'Germany'},
            {'wrong_key': 'France', 'gdp': '400'},
            {'country': 'Italy', 'wrong_value': '500'},
            {'not_a_dict': 'string'},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 1
        assert result[0]['Страна'] == 'USA'
        assert result[0]['Средний ВВП'] == 200.0

    def test_sorting(self):
        """Test descending sorting."""
        data = [
            {'country': 'A', 'gdp': '100'},
            {'country': 'B', 'gdp': '300'},
            {'country': 'C', 'gdp': '200'}
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert result[0]['Страна'] == 'B'
        assert result[1]['Страна'] == 'C'
        assert result[2]['Страна'] == 'A'

        assert result[0]['Средний ВВП'] > result[1]['Средний ВВП'] > result[2]['Средний ВВП']

    def test_multiple_entries_per_country(self):
        """Test with multiple entries per country."""
        data = [
            {'country': 'USA', 'gdp': '100'},
            {'country': 'USA', 'gdp': '200'},
            {'country': 'USA', 'gdp': '300'},
            {'country': 'Germany', 'gdp': '150'},
            {'country': 'Germany', 'gdp': '250'},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 2

        usa = next(r for r in result if r['Страна'] == 'USA')
        germany = next(r for r in result if r['Страна'] == 'Germany')

        assert usa['Средний ВВП'] == 200.0
        assert germany['Средний ВВП'] == 200.0

    def test_single_entry_per_country(self):
        """Test with single entry per country."""
        data = [
            {'country': 'USA', 'gdp': '100'},
            {'country': 'Germany', 'gdp': '200'},
            {'country': 'France', 'gdp': '300'},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 3
        assert result[0]['Средний ВВП'] == 300.0
        assert result[1]['Средний ВВП'] == 200.0
        assert result[2]['Средний ВВП'] == 100.0

    def test_all_invalid_data(self):
        """Test when all data is invalid."""
        data = [
            {'country': 'USA', 'gdp': 'invalid'},
            {'country': 'Germany', 'gdp': None},
            {'country': 'France', 'gdp': ''},
            {'wrong': 'data'},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert result == []

    def test_mixed_valid_and_invalid(self):
        """Test mix of valid and invalid data."""
        data = [
            {'country': 'USA', 'gdp': '100'},
            {'country': 'USA', 'gdp': 'invalid'},
            {'country': 'Germany', 'gdp': '200'},
            {'country': 'Germany', 'gdp': None},
            {'country': 'France', 'gdp': '300'},
            {'country': 'France', 'gdp': ''},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 3
        assert next(r for r in result if r['Страна'] == 'USA')['Средний ВВП'] == 100.0
        assert next(r for r in result if r['Страна'] == 'Germany')['Средний ВВП'] == 200.0
        assert next(r for r in result if r['Страна'] == 'France')['Средний ВВП'] == 300.0

    def test_large_numbers(self):
        """Test with large GDP numbers."""
        data = [
            {'country': 'USA', 'gdp': '25462'},
            {'country': 'USA', 'gdp': '23315'},
            {'country': 'China', 'gdp': '17963'},
            {'country': 'China', 'gdp': '17734'},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        assert len(result) == 2
        usa = next(r for r in result if r['Страна'] == 'USA')
        china = next(r for r in result if r['Страна'] == 'China')

        assert usa['Средний ВВП'] == (25462 + 23315) / 2
        assert china['Средний ВВП'] == (17963 + 17734) / 2
        assert result[0]['Средний ВВП'] > result[1]['Средний ВВП']

    def test_precision(self):
        """Test floating point precision."""
        data = [
            {'country': 'Test', 'gdp': '100.123456'},
            {'country': 'Test', 'gdp': '200.789012'},
        ]
        report = AverageGDPReport(data)
        result = report.generate()

        expected = (100.123456 + 200.789012) / 2
        assert result[0]['Средний ВВП'] == expected
