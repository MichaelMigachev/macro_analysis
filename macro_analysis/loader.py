import csv

class DataLoader:
    def load_files(self, file_paths):
        data = []
        for file_path in file_paths:
            try:
                with open(file_path, mode='r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    data.extend(reader)
            except FileNotFoundError:
                raise FileNotFoundError(f"Файл не найден: {file_path}")
            except Exception as e:
                raise Exception(f"Ошибка чтения файла {file_path}: {str(e)}")
        return data
