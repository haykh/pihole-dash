query_lookup = {
    1: "A",
    2: "AAAA",
    3: "ANY",
    4: "SRV",
    5: "SOA",
    6: "PTR",
    7: "TXT",
    8: "NAPTR",
    9: "MX",
    10: "DS",
    11: "RRSIG",
    12: "DNSKEY",
    13: "NS",
    14: "OTHER",
    15: "SVCB",
    16: "HTTPS"
}
query_lookup_r = {v: k for k, v in query_lookup.items()}

status_help = {
    '🛑Blocked': 'BLOCK',
    '🟢Allowed': 'ALLOW'
}

status_lookup = {
    'BLOCK': [1, 4, 5, 6, 7, 8, 9, 10, 11],
    'ALLOW': [2, 3, 12, 13, 14]
}
