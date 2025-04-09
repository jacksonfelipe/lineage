URL_RATE_LIMITS_DICT = {
    '/app/server/api/players-online/': {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pvp/':       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pk/':        {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-clan/':      {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-rich/':      {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
}
