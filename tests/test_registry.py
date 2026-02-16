"""Tests for the ReportRegistry."""
import pytest
from macro_analysis.registry import ReportRegistry
from macro_analysis.reports.average_gdp import AverageGDPReport


class TestReportRegistry:
    """Test cases for ReportRegistry class."""

    def test_get_report_existing(self):
        """Test getting existing report by name."""
        report_class = ReportRegistry.get_report('average-gdp')
        assert report_class == AverageGDPReport
        assert report_class is not None

    def test_get_report_nonexistent(self):
        """Test getting nonexistent report returns None."""
        report_class = ReportRegistry.get_report('nonexistent')
        assert report_class is None

    def test_get_report_with_different_names(self):
        """Test get_report with various report names."""
        # Existing report
        assert ReportRegistry.get_report('average-gdp') == AverageGDPReport

        # Nonexistent reports
        assert ReportRegistry.get_report('') is None
        assert ReportRegistry.get_report('gdp-average') is None
        assert ReportRegistry.get_report('test') is None
        assert ReportRegistry.get_report('123') is None

    def test_reports_dictionary_structure(self):
        """Test that _reports dictionary has correct structure."""
        assert hasattr(ReportRegistry, '_reports')
        assert isinstance(ReportRegistry._reports, dict)
        assert 'average-gdp' in ReportRegistry._reports

    def test_reports_dictionary_immutability(self):
        """Test that _reports dictionary can be accessed but not accidentally modified."""
        original_reports = ReportRegistry._reports.copy()

        # Try to modify through get_report (should not modify)
        ReportRegistry.get_report('average-gdp')

        assert ReportRegistry._reports == original_reports

    def test_get_report_returns_class_not_instance(self):
        """Test that get_report returns the class, not an instance."""
        report_class = ReportRegistry.get_report('average-gdp')
        assert report_class == AverageGDPReport
        assert not isinstance(report_class, AverageGDPReport)

        # Check that it's a class (can be instantiated)
        instance = report_class([])
        assert isinstance(instance, AverageGDPReport)

    def test_multiple_calls_return_same_class(self):
        """Test that multiple calls to get_report return the same class."""
        first_call = ReportRegistry.get_report('average-gdp')
        second_call = ReportRegistry.get_report('average-gdp')

        assert first_call is second_call  # Same object reference

    @pytest.mark.parametrize("report_name,expected", [
        ('average-gdp', AverageGDPReport),
        ('AVERAGE-GDP', None),  # Case-sensitive
        ('Average-Gdp', None),  # Case-sensitive
        (' average-gdp ', None),  # Spaces not trimmed
    ])
    def test_get_report_case_sensitivity(self, report_name, expected):
        """Test that report names are case-sensitive."""
        result = ReportRegistry.get_report(report_name)
        assert result == expected

    def test_reports_dict_not_empty(self):
        """Test that _reports dictionary is not empty."""
        assert len(ReportRegistry._reports) > 0
        assert 'average-gdp' in ReportRegistry._reports

    def test_reports_dict_contains_only_classes(self):
        """Test that _reports dictionary contains only class objects."""
        for report_name, report_class in ReportRegistry._reports.items():
            assert isinstance(report_class, type)  # Check it's a class
            assert hasattr(report_class, '__init__')  # Has constructor
            assert hasattr(report_class, 'generate') or hasattr(report_class, 'process')  # Has expected methods

    def test_get_report_with_none_input(self):
        """Test get_report with None as input."""
        result = ReportRegistry.get_report(None)
        assert result is None

    def test_get_report_with_non_string_input(self):
        """Test get_report with non-string input."""
    # Словари и списки нельзя использовать как ключи в словаре,
    # поэтому они вызовут TypeError при попытке поиска
    with pytest.raises(TypeError):
        ReportRegistry.get_report([])

    with pytest.raises(TypeError):
        ReportRegistry.get_report({})

    # Числа и булевы значения преобразуются в ключи,
    # но таких ключей нет в словаре, поэтому вернется None
    assert ReportRegistry.get_report(123) is None
    assert ReportRegistry.get_report(True) is None
