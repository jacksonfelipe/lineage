URL_RATE_LIMITS_DICT = {
    # APIs antigas (mantidas para compatibilidade)
    '/app/server/api/players-online/':             {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pvp/':                    {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-pk/':                     {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-clan/':                   {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-rich/':                   {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-online/':                 {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/top-level/':                  {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-ranking/':           {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-heroes/':            {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/olympiad-current-heroes/':    {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/grandboss-status/':           {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/siege/':                      {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/siege-participants/':         {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/app/server/api/boss-jewel-locations/':       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},

    # Novas APIs DRF
    '/api/v1/server/players-online/':                 {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-pvp/':                        {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-pk/':                         {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-clan/':                       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-rich/':                       {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-online/':                     {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/top-level/':                      {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/olympiad-ranking/':               {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/olympiad-heroes/':                {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/olympiad-current-heroes/':        {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/grandboss-status/':               {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/siege/':                          {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/siege-participants/':             {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},
    '/api/v1/server/boss-jewel-locations/':           {'rate': '30/m', 'key': 'ip', 'group': 'public-api'},

    # Outras APIs
    '/app/wallet/transfer/servidor/': {'rate': '5/m', 'key': 'user_or_ip', 'group': 'wallet-transfers'},
    '/app/wallet/transfer/jogador/':  {'rate': '5/m', 'key': 'user_or_ip', 'group': 'wallet-transfers'},
}
