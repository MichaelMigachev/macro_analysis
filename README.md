# Анализ макроэкономических данных

Проект для обработки CSV файлов с макроэкономическими данными.

## Установка
#### 1. Клонируйте репозиторий
 
https://github.com/MichaelMigachev/macro_analysis.git

#### 2. Создайте и активируйте виртуальное окружение
 
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

#### 3. Установите зависимости
 
pip install -r requirements.txt
 
## Запуск

python main.py --files data/data1.csv data/data2.csv --report average-gdp
