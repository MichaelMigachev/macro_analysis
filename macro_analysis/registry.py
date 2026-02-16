from macro_analysis.reports.average_gdp import AverageGDPReport


class ReportRegistry:
    _reports = {
        'average-gdp': AverageGDPReport
    }

    @classmethod
    def get_report(cls, report_name):
        return cls._reports.get(report_name)
