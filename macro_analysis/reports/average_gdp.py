from collections import defaultdict
from typing import List, Dict, Any, Union


class AverageGDPReport:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def generate(self) -> List[Dict[str, Union[str, float]]]:
        """
        Calculate average GDP for each country.

        Returns:
            List of dictionaries with 'Страна' and 'Средний ВВП',
            sorted by average GDP descending
        """
        gdp_data = defaultdict(list)

        for row in self.data:
            # Проверяем наличие обоих ключей
            if not isinstance(row, dict):
                continue

            if 'country' not in row or 'gdp' not in row:
                continue

            # Пропускаем None или пустые значения
            if row['gdp'] is None or row['gdp'] == '':
                continue

            try:
                gdp = float(row['gdp'])
                gdp_data[row['country']].append(gdp)
            except (ValueError, TypeError):
                # Пропускаем некорректные значения
                continue

        # Если нет данных, возвращаем пустой список
        if not gdp_data:
            return []

        result = [
            {
                'Страна': country,
                'Средний ВВП': sum(gdps) / len(gdps)
            }
            for country, gdps in gdp_data.items()
        ]

        return sorted(result, key=lambda x: x['Средний ВВП'], reverse=True)
