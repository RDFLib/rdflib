import sys

if sys.version_info < (2, 4, 1, 'alpha', 1):
    def rsplit(value, char=None, count=-1):
        # rsplit is not available in Python < 2.4a1
        if char is None:
            char = ' '
        parts = value.split(char)
        return [char.join(parts[:-count])] + parts[-count:]
else:
    from string import rsplit

