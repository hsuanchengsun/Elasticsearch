from naming_rules import NamingRules
from options_config import options_dict
from akeneo_setting import settings

from elasticsearch import Elasticsearch
from logzero import logger
import nltk

nltk.download("punkt")
from nltk.tokenize import word_tokenize
import re


class MasterItemProcessor:
    def __init__(self):
        self.options_dict = options_dict
        self.settings = settings

    def get_matches(self, product_name):
        client = Elasticsearch(
            [
                {
                    "host": settings["akeneo_es_host"],
                    "port": settings["akeneo_es_port"],
                    "scheme": settings["akeneo_es_scheme"],
                }
            ]
        )

        body = {
            "size": 100,
            "query": {
                "fuzzy": {
                    "values.product_name-text.<all_channels>.en_US": {
                        "value": product_name,
                        "fuzziness": "AUTO",
                        "rewrite": "top_terms_1",
                    }
                }
            },
        }
        response = client.search(
            index=settings["akeneo_es_index"], body=body, scroll="1m"
        )

        if not response["hits"]["hits"]:
            if "extraction" in product_name:
                new_product_name = product_name.replace("extraction", "Ext")
                body = {
                    "size": 100,
                    "query": {
                        "fuzzy": {
                            "values.product_name-text.<all_channels>.en_US": {
                                "value": new_product_name,
                                "fuzziness": "AUTO",
                                "rewrite": "top_terms_1",
                            }
                        }
                    },
                }
                response = client.search(
                    index=settings["akeneo_es_index"], body=body, scroll="1m"
                )
            else:
                pass
        # print(results)
        if response["hits"]["hits"]:
            print(
                "Find match for the product name in the original database. Please verify"
            )
            return (
                response["hits"]["hits"][0]["_source"]["identifier"],
                response["hits"]["hits"][0]["_source"]["values"]["product_name-text"],
            )
        else:
            print(
                "Does not find match. Generate a master item name. User can provide more details to custom the other master item name"
            )
            return product_name

    def nltk_name_parser(self, product_name):
        word_list = word_tokenize(product_name)
        return word_list

    def auto_criteria(self, parse_name):
        matches = {key: None for key in options_dict}

        for word in parse_name:
            for option_name, option_values in options_dict.items():
                if word in option_values:
                    matches[option_name] = word
                    break

        for option_name in matches:
            if matches[option_name] is None:
                matches[option_name] = options_dict[option_name]
        # print(matches)
        return matches

    def master_item_generate(self, parse_name, selected_values):
        processor = NamingRules(parse_name)
        result = processor.process_product(selected_values)
        result = [x for x in result if x is not None]
        master_item = " ".join(result)
        # print(master_item)
        return master_item

    def format_output(self, pre_format):
        pre_format = re.sub(r"(\w)\s*\.\s*(\w)", r"\1. \2", pre_format)
        pre_format = re.sub(r"(\d)\s*\.\s*(\d)", r"\1.\2", pre_format)
        pre_format = re.sub(r"\s*P\s*\.\s*E\s*\.", " P.E.", pre_format)
        pre_format = re.sub(r"\s*Ext\s*\.", " Ext.", pre_format)
        pre_format = re.sub(r"(\d)\s*%\s*", r"\1% ", pre_format)
        pre_format = re.sub(r"\( ", r"(", pre_format)
        pre_format = re.sub(r" \)", r")", pre_format)
        pre_format = pre_format.strip()
        return pre_format
