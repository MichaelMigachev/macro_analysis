import argparse
import tabulate
from macro_analysis.loader import DataLoader
from macro_analysis.registry import ReportRegistry


def main():
    parser = argparse.ArgumentParser(description='Макроэкономический анализ')
    parser.add_argument('--files', nargs='+', required=True, help='Список CSV файлов')
    parser.add_argument('--report', required=True, help='Тип отчета')

    args = parser.parse_args()

    try:
        loader = DataLoader()
        data = loader.load_files(args.files)

        report_cls = ReportRegistry.get_report(args.report)
        if not report_cls:
            raise ValueError(f"Неизвестный тип отчета: {args.report}")

        report = report_cls(data)
        result = report.generate()

        print(tabulate.tabulate(result, headers='keys', tablefmt='grid'))

    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == '__main__':
    main()
