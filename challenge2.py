from api2 import API2
from subprocess import Popen
import json
import logging


class Challenge:
    """Class Challenge to manage all the challenge operations"""

    def __init__(self):
        """Function to initialize the class

        Args:
            self: self class object
        """
        # Define class API
        self.api = API2()
        # Initialize a list of SAVED_OBJECTS (used in get_ancestors)
        self.SAVED_OBJECTS = []
        # Initialize the total number of objects
        self.total = 0

    def remove_duplicates(self, objects: list):
        # Filter list removing duplicates
        result = [
            item
            for index, item in enumerate(objects)
            if item not in objects[index + 1 :]
        ]
        return result

    def save_last_execution(self, last: int):
        try:
            base_path = "/tmp/last.bkp"
            file = open(base_path, "w")
            file.truncate()
            file.write(str(last))
            file.close()
        except Exception as err:
            logging.error(f"[ERROR] Couldn't save file. Traceback: {err}")
            return False
        else:
            return True

    def get_last_execution(self):
        try:
            base_path = "/tmp/last.bkp"
            file = open(base_path, "r")
            result = file.read()
            file.close()
        except FileNotFoundError as err:
            logging.error(f"[ERROR] File last.bkp not found. Traceback: {err}")
            return False
        else:
            return int(result)

    def get_products(self, filename: str):
        """Function to load json file into list to further manipulation

        Args:
            filename (str): The name of the JSON file with the products

        Returns:
            bool: Returns False if the file was not found
            products (list): Return the list with the products

        """
        try:
            file = open(filename, "r")
            products = json.load(file)
        except FileNotFoundError as err:
            logging.error(f"[ERROR] File {filename} not found. Traceback: {err}")
            return False
        else:
            return products

    def get_ancestors(self, products: list, product: dict):
        """Function to get all ancestor for given `product` on a `products` list

        Args:
            products (list): a list of all products to look up
            product (dict): the product dictionary which wants to find ancestors

        Returns:
            bool: False if some error occurred
            ancestors(list): a list with all ancestors names and ids

        """
        try:
            # Get the parent_id from the given product
            parent_identifier = product["parent_id"]
            # Get all items
            found = [item for item in products if item["id"] == parent_identifier]
            found = self.remove_duplicates(found)

            # Result list
            ancestors = []

            for item in found:
                # If item has a parent, search for its ancestors
                if item["parent_id"] is not None:
                    for result in self.get_ancestors(products, item):
                        ancestors.append(result)
                # For each item of the SAVED_OBJECTS look up for the info of the
                # ancestor
                for i in range(len(self.SAVED_OBJECTS)):
                    if self.SAVED_OBJECTS[i].get("name") == item["name"]:
                        ancestors.append(
                            {
                                "name": item["name"],
                                "id": self.SAVED_OBJECTS[i].get("id"),
                            }
                        )

            ancestors = self.remove_duplicates(ancestors)
        except Exception as err:
            logging.error(f"[ERROR] Error while searching ancestors. Traceback: {err}")
            return False
        else:
            return ancestors

    def filter_products(self, products: list):
        """Function to filter all products that does not have parent products

        Args:
            products (list): The list of products that want to filter

        Returns:
            independent (list): The list of products without parent

        """
        # Get all products that has no parent
        independent = [product for product in products if product["parent_id"] is None]
        # Get all products that has parent
        dependent = [
            product for product in products if product["parent_id"] is not None
        ]
        # Sort dependent products by parent_id, so that a child will be always
        # inserted after the parent
        dependent = sorted(dependent, key=lambda item: item["parent_id"])
        # Saves the total of objects
        self.total = len(independent) + len(dependent)
        return independent, dependent

    def save_independent_products(self, products: list):
        """Function to save products without parents

        Args:
            products (list): The list of products that want to be saved

        Returns:
            bool: True if all elements was inserted, otherwise False

        Raises:
            Exception: If the quantity of products stored isn't the same a the
            quantity of independents product

        """
        try:
            for product in products:
                # Creates each product in the API and saves it to SAVED_OBJECTS
                # to maintain the new ID for the ancestors
                last = self.get_last_execution()
                response = self.api.create(
                    data={"name": product["name"], "parent_id": None, "ancestors": None}
                )
                logging.info(f"[INFO] Object created: {response}")
                logging.info(f"[INFO] Storage size: {len(self.api._storage)}")
                self.SAVED_OBJECTS.append(response)
                self.save_last_execution(last + 1)

            if len(products) != len(self.api._storage):
                raise Exception(
                    f"Missing objects: Expected {len(products)} "
                    f"- Stored: {len(self.api._storage)}"
                )
        except Exception as err:
            logging.error(
                f"[ERROR] Error while saving independent products. Traceback: {err}"
            )
            return False
        else:
            return True

    def save_dependent_products(self, products: list, product_base: list):
        """Function to save products without parents

        Args:
            products (list): The list of products that want to be saved
            product_base (list): The list of all products (used on get_ancestors)

        Returns:
            bool: True if all elements was inserted, otherwise False

        Raises:
            Exception: If couldn't get the ancestors

            Exception: If the quantity of products stored isn't the same a the
            quantity of all products

        """
        try:
            for product in products:
                # Get all ancestors for each product
                ancestors = self.get_ancestors(product_base, product)
                if not ancestors:
                    raise Exception(
                        "Error while saving dependent products. Couldn't"
                        " execute get_ancestors(). Verify traceback."
                    )
                last = self.get_last_execution()
                # Creates each product in the API and saves it to SAVED_OBJECTS
                # to maintain the new ID for the ancestors
                response = self.api.create(
                    data={
                        "name": product["name"],
                        "parent_id": ancestors[0]["id"],
                        "ancestors": list(set([item["name"] for item in ancestors])),
                    }
                )
                logging.info(f"[INFO] Object created: {response}")
                logging.info(f"[INFO] Storage size: {len(self.api._storage)}")
                self.SAVED_OBJECTS.append(response)
                self.save_last_execution(last + 1)
            if self.total != len(self.api._storage):
                raise Exception(
                    f"Missing objects: Expected {len(product_base)} "
                    f"- Stored: {len(self.api._storage)}"
                )
        except Exception as err:
            logging.error(
                f"[ERROR] Error while saving dependent products. Traceback: {err}"
            )
            return False
        else:
            return True


logging.basicConfig(level=logging.ERROR, format="%(name)s: %(levelname)s - %(message)s")


def create_products():
    """
    Main function to execute the process
    """
    try:
        # Instantiate the class and separate objects into two lists
        challenge = Challenge()
        challenge.save_last_execution(0)
        product_base = challenge.get_products("product_groups.json")
        independent, dependent = challenge.filter_products(product_base)
        if not challenge.save_independent_products(independent):
            raise Exception

        if not challenge.save_dependent_products(dependent, product_base):
            raise Exception

    except Exception as err:
        logging.error(f"[ERROR] While processing the objects. Traceback: {err}")


def main():
    """
    Main function to execute the process
    """
    create_products()


if __name__ == "__main__":
    # Run main function
    main()
