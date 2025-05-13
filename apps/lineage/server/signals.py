from utils.dynamic_import import get_query_class
LineageAccount = get_query_class("LineageAccount")


LineageAccount.ensure_columns()
