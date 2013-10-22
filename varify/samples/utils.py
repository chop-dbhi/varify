import hashlib


def file_md5(f, size=8192):
    "Calculates the MD5 of a file."
    md5 = hashlib.md5()
    while True:
        data = f.read(size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()
