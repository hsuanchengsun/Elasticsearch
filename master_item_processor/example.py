#!/usr/bin/python
# -*- coding: utf-8 -*-

from masteritemprocessor import MasterItemProcessor


def main():
    # Use the class

    processor = MasterItemProcessor()

    # Input new product name

    product_name = ""

    # Match Process, fuzzy query with elastic search
    # If the code finds match, it returns match identifier and product name

    match_result = processor.get_matches(product_name)
    print(match_result)

    # If the code did not find match, it will return product name as default master item name
    # product_name = "Natural Vitamin E"
    # match_result = processor.get_matches(product_name)

    # If user decide not to use the master item name, then we enter auto process
    # Parse the product name into a list

    parse_name = processor.nltk_name_parser(product_name)
    print(parse_name)

    # Identify important criteria from product name and set the option with those values. Other criteria is still selectable

    user_gui = processor.auto_criteria(parse_name)
    print(user_gui)


    # Create final master item name

    master_item_pre = processor.master_item_generate(parse_name, user_decision)
    master_item = processor.format_output(master_item_pre)
    print(master_item)


if __name__ == "__main__":
    main()
