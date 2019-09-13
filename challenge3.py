from api3 import API3
import json
import logging
import os


class Challenge:
    """Class Challenge to manage all the challenge operations"""

    def __init__(self):
        """Function to initialize the class

        Args:
            self: self class object
        """
        # Define class API
        self.api = API3()
        # Initialize a list of SAVED_OBJECTS (used in get_ancestors)
        self.SAVED_OBJECTS = []
        # Initialize the total number of objects
        self.total = 0
        # Load saved objects from file to continue the last execution
        self.load_saved_objects()
        # Define a package size for bulk operations
        # PS: The bigger the package is, fewer operations the API will make,
        # consequently, fewer crashes will happen and fewer accesses to the
        # backup files, speeding up the API
        self.PACKAGE_SIZE = 13100

    def remove_duplicates(self, objects: list):
        """Function to remove identical objects from list

        Args:
            objects (list): List with objects to verify duplicates

        Returns:
            result (list): List without duplicated objects

        """
        # Filter list removing duplicates
        result = [
            item
            for index, item in enumerate(objects)
            if item not in objects[index + 1 :]
        ]
        return result

    def get_saved_objects(self):
        """Function to get the previous saved objects from backup file

        Returns:
            bool: Returns False if couldn't load the objects
            result (list): Returns a list with all the previous objects

        """
        try:
            base_path = "/tmp/objects.bkp"
            # Open backup file for read and gets the string with all saved objects
            file = open(base_path, "r")
            result = file.read()
            file.close()
        except Exception as err:
            logging.error(f"[ERROR] Couldn't save file. Traceback: {err}")
            return False
        else:
            # Parse the string into list of objects with JSON
            return json.loads(result)

    def load_saved_objects(self):
        """Function to get the backup objects and save it in SAVED_OBJECTS

        Returns:
            bool: Returns False if couldn't load the objects, otherwise True

        """
        try:
            # Get all saved objects from backup file
            objects = self.get_saved_objects()
            # Adds the objects to SAVED_OBJECTS
            for item in objects:
                self.SAVED_OBJECTS.append(item)
        except Exception as err:
            logging.error(f"[ERROR] Couldn't load objects. Traceback: {err}")
            return False
        else:
            return True

    def save_objects(self):
        """Function to save execution objects into a backup file

        Returns:
            bool: True if the objects were saved, otherwise False

        """
        try:
            base_path = "/tmp/objects.bkp"
            # Open backup file for write
            file = open(base_path, "w")
            # Remove old content from file
            file.truncate()
            # Write a string with the execution objects
            file.write(json.dumps(self.SAVED_OBJECTS))
            file.close()
        except Exception as err:
            logging.error(f"[ERROR] Couldn't save file. Traceback: {err}")
            return False
        else:
            return True

    def save_last_execution(self, last: int):
        """Function the save the number of objects saved in the last execution

        Returns:
            bool: False if couldn save the number of the last execution, otherwise True

        """
        try:
            base_path = "/tmp/last.bkp"
            # Open backup file for write
            file = open(base_path, "w")
            # Remove the old number of objects saved
            file.truncate()
            # Writes the new number
            file.write(str(last) + "\n")
            file.close()
        except Exception as err:
            logging.error(f"[ERROR] Couldn't save file. Traceback: {err}")
            return False
        else:
            return True

    def get_last_execution(self):
        """Function to get the number of saved objects from last execution

        Returns:
            bool: False if couldn't find the backup file
            result (int): The number of saved objects

        """
        try:
            base_path = "/tmp/last.bkp"
            # Open backup file for read and gets the string the number os saved objects
            # from last execution
            file = open(base_path, "r")
            result = file.read()
            file.close()
        except FileNotFoundError as err:
            logging.error(f"[ERROR] File last.bkp not found. Traceback: {err}")
            return False
        else:
            # Remove the EOL and convert to int before returning
            return int(result.strip("\n"))

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

    def transform_package(self, package: list):
        """Function to transform objects from old format to the new API format

        Args:
            package(list):
        Returns:
            bool: False if some error occurred during the transformation
            transformed_package (list): List of items with the new format

        """
        try:
            # Initialize the new package to respond
            transformed_package = []
            # Iterates in every item in the package
            for item in package:
                name = item["name"]
                identifier = item["parent_id"]
                # If has parent, set its ancestors
                if identifier:
                    ancestors = item["ancestors"]
                else:
                    ancestors = None
                # Create the new object and adds to the response package
                data = {"name": name, "parent_id": identifier, "ancestors": ancestors}
                transformed_package.append(data)

        except Exception as err:
            logging.error(f"[ERROR] Error while transforming package. Traceback{err}")
            return False
        else:
            return transformed_package

    def save_independent_products(self, products: list):
        """Function to save products without parents

        Args:
            products (list): The list of products that want to be saved

        Returns:
            bool: True if all elements was inserted, otherwise False

        Raises:
            Exception: If the quantity of products stored isn't the same a the
            quantity of independents product
            Exception: If can't transform a package of products to the new format

        """
        try:
            size_independent_products = len(products)
            # Gets the size of products already saved
            objects_saved = self.get_last_execution()
            # If more than the products to save then all independent products
            # were already saved
            if objects_saved > len(products):
                return True
            else:
                # Otherwise remove the first size(objects_saved) from products list
                products = products[objects_saved:]

            while True:
                # Resize the products to PACKAGE_SIZE
                package = products[: self.PACKAGE_SIZE]
                last = self.get_last_execution()
                # Transform dictionaries objects to the new format
                package = self.transform_package(package)
                # If package is False, some error occurred during transformation
                if not package:
                    raise Exception(
                        "An error occurred on transform_package()."
                        "Check the traceback."
                    )
                # Bulk create objects
                response = self.api.bulk_create(package)

                # Save the created objects
                for item in response:
                    self.SAVED_OBJECTS.append(item)

                logging.info(f"[INFO] Objects created: {response}")
                logging.info(f"[INFO] Storage size: {len(self.SAVED_OBJECTS)}")

                # Saves the number of saved objects and objects into the backup file
                self.save_last_execution(last + len(package))
                self.save_objects()
                # Resize the remaining products
                products = products[self.PACKAGE_SIZE :]

                # If zero products, break the loop
                if not len(products):
                    break

            if size_independent_products != len(self.SAVED_OBJECTS):
                raise Exception(
                    f"Missing objects: Expected {size_independent_products} "
                    f"- Stored: {len(self.SAVED_OBJECTS)}"
                )
        except Exception as err:
            logging.error(
                f"[ERROR] Error while saving independent products. Traceback: {err}"
            )
            return False
        else:
            return True

    def save_dependent_products(
        self, products: list, product_base: list, size_independent: int
    ):
        """Function to save products without parents

        Args:
            products (list): The list of products that want to be saved
            product_base (list): The list of all products (used on get_ancestors)
            size_independent: The size of independent products (shloud be already saved)

        Returns:
            bool: True if all elements was inserted, otherwise False

        Raises:
            Exception: If couldn't get the ancestors

            Exception: If the quantity of products stored isn't the same a the
            quantity of all products
            Exception: If can't transform a package of products to the new format

        """
        try:
            size_all_products = len(product_base)
            # Gets the size of products already saved
            objects_saved = self.get_last_execution()
            # If more than the products to save then all independent products
            # were already saved
            if objects_saved > len(product_base):
                return True
            else:
                # Otherwise remove the first size(objects_saved - independent) from
                # products list
                products = products[objects_saved - size_independent :]

            while True:
                # Resize the products to PACKAGE_SIZE
                package = products[: self.PACKAGE_SIZE]
                last = self.get_last_execution()
                # Search for ancestors of the items and adds the key with them
                # onto the dictionary
                for i in range(len(package)):
                    ancestors = self.get_ancestors(product_base, package[i])
                    # If False some error occurred while searching
                    if not ancestors:
                        raise Exception(
                            "Error while saving dependent products. Couldn't"
                            " execute get_ancestors(). Verify traceback."
                        )
                    else:
                        package[i]["ancestors"] = ancestors
                # Transform dictionaries objects to the new format
                package = self.transform_package(package)
                # If package is False, some error occurred during transformation
                if not package:
                    raise Exception(
                        "An error occurred on transform_package()."
                        "Check the traceback."
                    )

                # Bulk create objects
                response = self.api.bulk_create(package)
                # Save the created objects
                for item in response:
                    self.SAVED_OBJECTS.append(item)

                logging.info(f"[INFO] Objects created: {response}")
                logging.info(f"[INFO] Storage size: {len(self.SAVED_OBJECTS)}")

                # Saves the number of saved objects and objects into the backup file
                self.save_last_execution(last + len(package))
                self.save_objects()
                # Resize the remaining products
                products = products[self.PACKAGE_SIZE :]

                # If zero products, break the loop
                if not len(products):
                    break

            if size_all_products != len(self.SAVED_OBJECTS):
                raise Exception(
                    f"Missing objects: Expected {size_all_products} "
                    f"- Stored: {len(self.SAVED_OBJECTS)}"
                )
        except Exception as err:
            logging.error(
                f"[ERROR] Error while saving dependent products. Traceback: {err}"
            )
            return False
        else:
            return True


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(name)s: %(levelname)s - %(message)s")


def create_products():
    """
    Function to save all the products

    Returns:
        bool: True if executed without errors, otherwise False

    """
    try:
        # Instantiate the class and separate objects into two lists
        challenge = Challenge()
        # Get all products
        product_base = challenge.get_products("product_groups.json")
        # Divide the products into independent (no parent) and dependent (with parents)
        independent, dependent = challenge.filter_products(product_base)
        if not challenge.save_independent_products(independent):
            Exception("Function save_independent_products() couldn't complete")

        if not challenge.save_dependent_products(
            dependent, product_base, len(independent)
        ):
            raise Exception("Function save_dependent_products() couldn't complete")

    except Exception as err:
        logging.error(f"[ERROR] While processing the objects. Traceback: {err}")
        return False
    else:
        return True


def main():
    """
    Main function to execute the process
    """
    challenge = Challenge()
    # Get the number of saved files on last execution
    last_saved = challenge.get_last_execution()
    # Get the total of products to save
    total_objects = len(challenge.get_products("product_groups.json"))

    # While there are products to be saved
    while last_saved < total_objects:
        create_products()
        # Updates last_saved number
        last_saved = challenge.get_last_execution()

    logging.info("[INFO] Execution done with no errors!")
    # Sends to runner a signal different from the crash signal
    # Indicates terminated execution
    os._exit(1)


if __name__ == "__main__":
    # Run main function
    main()
