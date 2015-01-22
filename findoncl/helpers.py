

def absurl(domain, path, protocol='http'):
    if '://' not in domain:
        url = '%s://%s' % (protocol, domain)
    else:
        url = domain

    if url.endswith('/'):
        url = url[:-1]

    if not path.startswith('/'):
        path = '/%s' % path

    return "%s%s" % (url, path)

