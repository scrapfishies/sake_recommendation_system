'''
Functions to clean text
'''

import numpy as np
import re
import string
import unicodedata


def remove_accented_chars(text):
    '''
    Function to replace accented chars with non-accented chars
    '''
    clean_text = unicodedata.normalize('NFKD', text).encode(
        'ascii', 'ignore').decode('utf-8', 'ignore')
    return clean_text


def remove_punctuation(text):
    '''
    Function to remove punctuation from string
    '''
    text = re.sub(
        '/', '  ', text)  # This helps to keep wines pairs from concatenating
    clean_text = ''.join([c for c in text if c not in string.punctuation])
    return clean_text


def clean_text(text):
    '''
    Cleans text:
    - calls on remove_accented_chars
    - calls on remove_punctiontion
    - lowercases
    - strips leading/trailing whitespace and fixes doublespaces
    '''
    clean_text = remove_punctuation(remove_accented_chars(text)).lower()
    # Remove double spacing and padded spacing
    clean_text = re.sub('  ', ' ', clean_text).strip()
    return clean_text


def split_on_chars(chars, text):
    '''
    Function to correct scraped text inconsistencies
    ----------------
    Calls on clean_text (and its associates)
    Inputs: Text, and string to split on (as chars)
    Outputs: clean text or np.nan for missing data
    '''
    if text is not None:
        if chars in text:
            return text.split(chars)[0]
        else:
            return text
    else:
        return 'none'
