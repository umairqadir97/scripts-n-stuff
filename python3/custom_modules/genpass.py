# Python modules to generate passwords
# password types: alpha numeric, random characters, xkcd

# import common modules
import string, secrets, requests

# alpha numeric
def alpha_numeric(LEN):
    if type(LEN) is not int:
        return False
    pool = string.ascii_letters + string.digits
    while True:
        result = ''.join(secrets.choice(pool) for X in range(LEN))
        if (any(X.islower() for X in result)
                and any(X.isupper() for X in result)
                and sum(X.isdigit() for X in result) >= 3):
            break
    return result

# random characters
def random_characters(LEN):
    if type(LEN) is not int:
        return False
    pool = string.ascii_letters + string.digits + string.punctuation
    while True:
        result = ''.join(secrets.choice(pool) for X in range(LEN))
        if (any(X.islower() for X in result)
                and any(X.isupper() for X in result)
                and sum(X.isdigit() for X in result) >= 3
                and [X in string.punctuation for X in result].count(True) <= 5):
            break
    return result

# xkcd
def xkcd(LEN):
    if type(LEN) is not int:
        return False
    get_words = 'https://www.mit.edu/~ecprice/wordlist.10000'
    response = requests.get(get_words)
    word_list = [X.decode('utf-8') for X in response.content.splitlines()]
    return ' '.join(secrets.choice(word_list) for X in range(LEN))
