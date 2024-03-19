import os
import webbrowser
class FileManager:
    @staticmethod
    def list_all_files_in_folder(folder_path):
        try:
            abs_path = os.path.join(os.getcwd(), folder_path)
            files = os.listdir(abs_path)
            for file in files:
                print(file)
        except OSError as e:
            print(f"Error while listing files: {e}")

    @staticmethod
    def read_file_content(folder_path, file_name):
        try:
            abs_path = os.path.join(os.getcwd(), folder_path, file_name)
            with open(abs_path, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found at path: {abs_path}")
        except Exception as e:
            print(f"Exception while reading file: {e}")

    @staticmethod
    def save_file_content(folder_path, file_name, binary_content):
        try:
            abs_path = os.path.join(os.getcwd(), folder_path, file_name)
            with open(abs_path, 'wb') as file:
                file.write(binary_content)
            print(f"File saved successfully at: {abs_path}")
        except Exception as e:
            print(f"Error while saving file: {e}")

    @staticmethod
    def open_media_file_in_browser(folder_path, file_name):
        try:
            abs_path = os.path.join(os.getcwd(), folder_path, file_name)
            webbrowser.open(abs_path)
        except Exception as e:
            print(f"Error while opening media file: {e}")

    @staticmethod
    def file_exists(folder_path, file_name):
        abs_path = os.path.join(os.getcwd(), folder_path, file_name)
        return os.path.exists(abs_path)
