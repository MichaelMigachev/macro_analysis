"""Tests for the CLI module."""
import pytest
import sys
from unittest.mock import patch, MagicMock
from io import StringIO
from pathlib import Path

from macro_analysis.cli import main


class TestCLI:
    """Test cases for CLI module."""

    def test_main_success_with_valid_data(self, tmp_path):
        """Test successful execution with valid data."""
        # Create test CSV file
        test_file = tmp_path / "test.csv"
        test_file.write_text("""country,year,gdp,gdp_growth,inflation,unemployment,population,continent
USA,2023,100,1.0,2.0,3.0,100,NA""", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'USA' in output
                assert '100' in output

    def test_main_with_multiple_files(self, tmp_path):
        """Test with multiple CSV files."""
        # Create test files
        file1 = tmp_path / "file1.csv"
        file1.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        file2 = tmp_path / "file2.csv"
        file2.write_text("country,gdp\nGermany,200\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(file1), str(file2), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'USA' in output
                assert 'Germany' in output

    def test_main_file_not_found(self):
        """Test with non-existent file."""
        test_args = ['program.py', '--files', 'nonexistent.csv', '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'Ошибка' in output
                assert 'Файл не найден' in output

    def test_main_invalid_report_type(self, tmp_path):
        """Test with invalid report type."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'invalid']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'Ошибка' in output
                assert 'Неизвестный тип отчета' in output

    def test_main_missing_files_argument(self):
        """Test with missing --files argument."""
        test_args = ['program.py', '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

    def test_main_missing_report_argument(self, tmp_path):
        """Test with missing --report argument."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file)]

        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()

    def test_main_empty_file(self, tmp_path):
        """Test with empty CSV file."""
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("", encoding='utf-8')

        test_args = ['program.py', '--files', str(empty_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Пустой вывод или пустая строка
                assert output == '' or output == '\n' or 'Страна' in output

    def test_main_with_malformed_csv(self, tmp_path):
        """Test with malformed CSV file."""
        malformed_file = tmp_path / "malformed.csv"
        malformed_file.write_text("country,gdp\nUSA\n", encoding='utf-8')  # Missing gdp value

        test_args = ['program.py', '--files', str(malformed_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Может быть ошибка или пустой вывод
                assert output != ''  # Проверяем, что что-то выводится

    def test_main_with_unicode_data(self, tmp_path):
        """Test with Unicode characters in data."""
        test_file = tmp_path / "unicode.csv"
        test_file.write_text("country,gdp\nFrançe,100\nРоссия,200\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'Françe' in output
                assert 'Россия' in output

    def test_main_with_large_numbers(self, tmp_path):
        """Test with large GDP numbers."""
        test_file = tmp_path / "large.csv"
        test_file.write_text("country,gdp\nUSA,25462\nChina,17963\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert '25462' in output
                assert '17963' in output

    @patch('macro_analysis.loader.DataLoader.load_files')
    def test_main_with_loader_exception(self, mock_load, tmp_path):
        """Test when loader raises an exception."""
        mock_load.side_effect = Exception("Loader error")

        test_file = tmp_path / "test.csv"
        test_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'Ошибка' in output
                assert 'Loader error' in output

    @patch('macro_analysis.registry.ReportRegistry.get_report')
    def test_main_with_registry_returning_none(self, mock_get_report, tmp_path):
        """Test when registry returns None (report not found)."""
        mock_get_report.return_value = None

        test_file = tmp_path / "test.csv"
        test_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'nonexistent']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'Неизвестный тип отчета' in output

    @patch('macro_analysis.reports.average_gdp.AverageGDPReport.generate')
    def test_main_with_report_generate_exception(self, mock_generate, tmp_path):
        """Test when report.generate() raises an exception."""
        mock_generate.side_effect = Exception("Generate error")

        test_file = tmp_path / "test.csv"
        test_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                assert 'Ошибка' in output
                assert 'Generate error' in output

    def test_main_with_no_data_after_processing(self, tmp_path):
        """Test when all data is invalid and nothing to display."""
        test_file = tmp_path / "invalid.csv"
        test_file.write_text("country,gdp\nUSA,invalid\nGermany,none\n", encoding='utf-8')

        test_args = ['program.py', '--files', str(test_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Пустой вывод или пустая строка
                assert output == '' or output == '\n' or 'Страна' in output

    def test_main_with_different_encodings(self, tmp_path):
        """Test with files in different encodings."""
        # UTF-8 file
        utf8_file = tmp_path / "utf8.csv"
        utf8_file.write_text("country,gdp\nUSA,100\n", encoding='utf-8')

        # CP1251 file (Russian Windows)
        cp1251_file = tmp_path / "cp1251.csv"
        cp1251_file.write_text("country,gdp\nРФ,200\n", encoding='cp1251')

        test_args = ['program.py', '--files', str(utf8_file), str(cp1251_file), '--report', 'average-gdp']

        with patch.object(sys, 'argv', test_args):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                main()
                output = mock_stdout.getvalue()
                # Должна быть ошибка о кодировке
                assert 'Ошибка' in output or 'codec' in output or 'encoding' in output.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
