from api1 import API1
import json
import logging


class Challenge:
    """Class Challenge to manage all the challenge operations"""

    def __init__(self):
        """Function to initialize the class

        Args:
            self: Self class object
        """
        self.api = API1()

    def get_products(self, filename: str):
        """Function to load json file into list to further manipulation

        Args:
            filename (str): The name of the JSON file with the products

        Returns:
            bool: Returns False if the file was not found
            products (list): Return the list with the products

        Raises:
            FileNotFoundError: If the `filename` file was not found

        """
        try:
            file = open(filename, "r")
            products = json.load(file)
        except FileNotFoundError as err:
            logging.error(f"[ERROR] File {filename} not found. Traceback: {err}")
            return False
        else:
            return products

    def filter_independent_products(self, products: list):
        """Function to filter all products that does not have parent products

        Args:
            products (list): The list of products that want to filter

        Returns:
            independent (list): The list of products without parent

        """
        independent = [product for product in products if product["parent_id"] is None]
        return independent

    def save_independent_products(self, products: list):
        """Function to save products without parents

        Args:
            products (list): The list of products that want to be saved

        Returns:
            bool: True if all elements was inserted, otherwise False

        """
        for product in products:
            response = self.api.create(
                data={"name": product["name"], "parent_id": None, "ancestors": None}
            )
            logging.info(f"[INFO] Object created: {response}")
            logging.debug(f"[DEBUG] Storage size: {len(self.api._storage)}")
        return response


logging.basicConfig(level=logging.DEBUG, format="%(name)s: %(levelname)s - %(message)s")

