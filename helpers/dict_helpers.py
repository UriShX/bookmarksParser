# dict_helpers
from functools import reduce
import operator

def get_recursively(search_dict:dict, field):
    """
    https://stackoverflow.com/a/20254842
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


def return_all_dict_values(dict_to_parse:dict):
    _list = []
    
    for v in dict_to_parse.values():
        if not type(v) == list:
            _list.append(v)
        else:
            for i in v:
                _list.append(i)

    return _list


def breadcrumb(json_dict_or_list:(dict or list), value):
  """
  https://stackoverflow.com/a/65979157
  returns breadcrumb of keys to given value
  """
  if json_dict_or_list == value:
    return [json_dict_or_list]
  elif isinstance(json_dict_or_list, dict):
    for k, v in json_dict_or_list.items():
      p = breadcrumb(v, value)
      if p:
        return [k] + p
  elif isinstance(json_dict_or_list, list):
    lst = json_dict_or_list
    for i in range(len(lst)):
      p = breadcrumb(lst[i], value)
      if p:
        return [i] + p


def get_nested(keys, data):
    return reduce(operator.getitem, keys, data)
