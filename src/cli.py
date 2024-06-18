
import os
from typing import List, Tuple, Optional
from prompt_toolkit.shortcuts import radiolist_dialog
from models.OpenModel import OpenModel

class FileManager:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.model = OpenModel()

    def list_files(self) -> List[str]:
        files = os.listdir(self.directory)
        txt_files = [f for f in files if f.endswith('.txt')]
        return txt_files

    def select_file(self, files: List[str]) -> Optional[str]:
        if not files:
            print("В директории нет .txt файлов.")
            return None
        choices = [(filename, filename) for filename in files]
        result = radiolist_dialog(
            title="Выберите файл",
            text="Доступные файлы:",
            values=choices
        ).run()
        return result

    def process_file_selection(self) -> None:
        files = self.list_files()
        selected_file = self.select_file(files)
        if selected_file:
            self.model.send_file(os.path.join(self.directory, selected_file))
            print(f"Выбран файл: {selected_file}")
        else:
            print("Файл не выбран")

def main() -> None:
    directory = 'docs/txt'
    file_manager = FileManager(directory)
    file_manager.process_file_selection()

if __name__ == "__main__":
    main()