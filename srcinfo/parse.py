from parse import parse, findall

arrays = [ 'pkgname', 'arch', 'license', 'groups', 'options',
           'conflicts', 'provides', 'replaces',
           'source', 'noextract', 'backup', 'validpgpkeys',
           'md5sums', 'sha1sums', 'sha256sums', 'sha384sums', 'sha512sums',
           'depends', 'makedepends', 'checkdepends','optdepends', ]


def remove_empty_values(values):
    return [v for v in values if v.strip()]


##
# Check if SRCINFO key is an array
#
def is_array(key):
    if key in arrays:
        return True
    for array in arrays:
        if key.startswith(array):
            return True
    return False


##
# Insert `value` into the array index `key` in list `target`
#
def insert_array(key, value, target):
    if key not in target:
            target[key] = []

    # Don't append value if already in the list
    if value not in target[key]:
        if value:
            target[key].append(value)


##
# Extract all SRCINFO variables from `string`, using `base` to look up default
# values.
#
def extract_vars(string, base={}):
    info = {}
    errors = []
    for line in string.splitlines():
        parsed = parse('{} ={}', line.lstrip())
        if parsed:
            key, value = parsed
        elif line.lstrip().startswith('#'):
            continue
        else:
            errors.append('failed to parse line: \'{}\''.format(line.lstrip()))
            continue

        value = value.strip()
        if is_array(key):
            insert_array(key, value, info)
        else:
            info[key] = value

    return (info, errors)

##
# Parse SRCINFO from string
#
# Returns a tuple of the srcinfo dict and an array of any errors found while
# parsing
#
def parse_srcinfo(source):
    sections = remove_empty_values(source.split('\n\n'))
    errors = []

    info, err = extract_vars(sections[0])
    errors += err

    if len(sections) >= 2:
        packages = info['packages'] = {}
        pkgs = sections[1:]
        for pkg in pkgs:
            package, err = extract_vars(pkg, info)
            errors += err
            packages[package['pkgname'][0]] = package

    return (info, errors)