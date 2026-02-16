from collections import defaultdict


class AverageGDPReport:
    def __init__(self, data):
        self.data = data

    def generate(self):
        gdp_data = defaultdict(list)

        for row in self.data:
            try:
                gdp = float(row['gdp'])
                gdp_data[row['country']].append(gdp)
            except ValueError:
                continue

        result = [
            {
                'Страна': country,
                'Средний ВВП': sum(gdps) / len(gdps)
            }
            for country, gdps in gdp_data.items()
        ]

        return sorted(result, key=lambda x: x['Средний ВВП'], reverse=True)
