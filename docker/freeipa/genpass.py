# Python modules to generate passwords
# password types: alpha numeric, random characters, xkcd

# import common modules
import string, secrets, requests

# alpha numeric
def alpha_numeric(LEN):
    '''
    Outputs password LEN characters long composed of lowercase, uppercase, and numbers.
    genpass.alpha_numeric(LEN)
    LEN: Integer, how many characters long you want your password to be.
    Output: String, or False on failure.
    '''
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
    '''
    Outputs password LEN characters long composed of lowercase, uppercase, numbers, and symbols.
    genpass.random_characters(LEN)
    LEN: Integer, how many characters long you want your password to be.
    Output: String, or False on failure.
    '''
    symbol_list = '@$%^&()[]><*?'
    if type(LEN) is not int:
        return False
    pool = string.ascii_letters + string.digits + symbol_list
    while True:
        result = ''.join(secrets.choice(pool) for X in range(LEN))
        if (any(X.islower() for X in result)
                and any(X.isupper() for X in result)
                and sum(X.isdigit() for X in result) >= 3
                and [X in string.punctuation for X in result].count(True) <= 3):
            break
    return result

# xkcd
def xkcd(LEN):
    '''
    Outputs XKCD style password composed of LEN amount of words, seperated by spaces.
    Requires internet access.
    genpass.xkcd(LEN)
    LEN: Integer, how many random words you want in your password.
    Output: String, or False on failure.
    '''
    if type(LEN) is not int:
        return False
    get_words = 'https://www.mit.edu/~ecprice/wordlist.10000'
    response = requests.get(get_words)
    word_list = [X.decode('utf-8') for X in response.content.splitlines()]
    return ' '.join(secrets.choice(word_list) for X in range(LEN))
