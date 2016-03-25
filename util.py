def num_or(n):
    if isinstance(n, str) and len(n) > 0:
        return int(n)
    return n
