def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G'}
    while size > power:
        size /= power
        n += 1
    return power_labels[n]+'B'

print(format_bytes(1084556))