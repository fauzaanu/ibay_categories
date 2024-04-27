import logging
import random
from time import sleep
import requests
import json


def get_categories(url, max_attempts=5):
    """
    Function to fetch categories from a given URL with retry logic
    """
    for attempt in range(max_attempts):
        try:
            duration = random.uniform(0.1, 0.3)
            sleep(duration)
            logging.info(f"Sleeping for {duration} seconds")

            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            response.raise_for_status()  # Raises an HTTPError if the response was unsuccessful
            txt = response.text
            if txt == "":
                raise requests.exceptions.RequestException("Empty response")
            return json.loads(response.text)
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Error occurred: {err}")
            if attempt < max_attempts - 1:  # Don't log for the last attempt
                logging.info(f"Retrying... Attempt {attempt + 1} of {max_attempts}")
            else:
                logging.error("Max attempts reached. Giving up.")
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON response")
            if attempt < max_attempts - 1:  # Don't log for the last attempt
                logging.info(f"Retrying... Attempt {attempt + 1} of {max_attempts}")
            else:
                logging.error("Max attempts reached. Giving up.")
    return []


# Function to build the category structure
def build_category_structure(initial_categories):
    final_categories = {}
    for category, id in initial_categories.items():
        logging.info(f"Processing {category}, ({id})")
        level1_categories = get_categories(f"https://ibay.com.mv/index.php?page=cat_ajax&id={id}")

        # Initialize the list for the current level 1 category
        final_categories[category] = []

        for l1_item in level1_categories:
            for l1_sub_id, l1_sub_name in l1_item.items():
                logging.info(f"Processing {l1_sub_name}, ({l1_sub_id})")
                level2_categories = get_categories(f"https://ibay.com.mv/index.php?page=cat_ajax&id={l1_sub_id}")

                # Initialize the dictionary for the current level 2 category
                level2_dict = {l1_sub_name: []}

                for l2_item in level2_categories:
                    for l2_sub_id, l2_sub_name in l2_item.items():
                        logging.info(f"Processing {l2_sub_name}, ({l2_sub_id})")
                        level3_categories = get_categories(
                            f"https://ibay.com.mv/index.php?page=cat_ajax&id={l2_sub_id}")

                        # Append level three categories as strings directly to the list under the level 2 category
                        for l3_item in level3_categories:
                            for l3_sub_id, l3_sub_name in l3_item.items():
                                level2_dict[l1_sub_name].append(l3_sub_name)

                # Add the level 2 category dictionary to the level 1 category list
                final_categories[category].append(level2_dict)

    return final_categories


def convert_empty_lists_to_strings(categories):
    """
    Converts empty lists in level 1 and level 2 categories to strings.
    """
    for category, level1_items in categories.items():
        # Check if the list of level 1 items is empty
        if not level1_items:
            categories[category] = category  # Replace the empty list with the level 1 name
        else:
            for level1_item in level1_items:
                for level2_name, level2_items in level1_item.items():
                    # Check if the list of level 2 items is empty
                    if not level2_items:
                        level1_item[level2_name] = level2_name  # Replace the empty list with the level 2 name
    return categories


# Function to save the modified structure to a new file
def save_modified_structure(categories, filename):
    """
    Saves the modified category structure to a new file.
    """
    with open(filename, "w") as f:
        json.dump(categories, f, indent=4)


if __name__ == "__main__":
    initial_categories = {
        "For Sale": "600",
        "Housing & Real Estate": "19",
        "Jobs": "55",
        "Services": "28",
        "Wanted": "87",
        "Business Opportunities": "176",
        "Announcements & Events": "227",
        "Free Stuff": "451"
    }

    logging.basicConfig(level=logging.ERROR)

    final_categories = build_category_structure(initial_categories)

    # Write the final dictionary to a JSON file
    with open("categories_final.json", "w") as f:
        json.dump(final_categories, f, indent=4)

    # Assuming final_categories is already defined and populated
    modified_categories = convert_empty_lists_to_strings(final_categories)
    save_modified_structure(modified_categories, "modified_categories_final.json")
