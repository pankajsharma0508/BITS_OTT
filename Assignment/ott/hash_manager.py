import hashlib


class HashManager:
    @staticmethod
    def calculate_hash(file_content):
        """
        Calculate the SHA-256 hash of the file content.

        Args:
            file_content (bytes): The content of the file as bytes.

        Returns:
            str: The hexadecimal representation of the hash.
        """
        hasher = hashlib.sha256()
        hasher.update(file_content)
        return hasher.hexdigest()

    @staticmethod
    def generate_file_hash(file_content):
        """
        Generate a unique hash for the file content.

        Args:
            file_content (bytes): The content of the file as bytes.

        Returns:
            str: The unique hash generated for the file content.
        """
        return HashManager.generate_file_hash(file_content)
