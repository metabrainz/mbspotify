from __future__ import print_function
from datetime import datetime
from flask import current_app
import io
import errno
import os
import psycopg2
import subprocess
import tarfile


DUMP_LICENSE_FILE_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "..", "licenses", "COPYING-PublicDomain"
)

_TABLES = {
    "mapping": (
        "id",
        "mbid",
        "spotify_uri",
        "cb_user",
        "is_deleted",
    ),
    "mapping_vote": (
        "id",
        "mapping",
        "cb_user",
    ),
}


def create_path(path):
    """Creates a directory structure if it doesn't exist yet."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise Exception("Failed to create directory structure %s. "
                            "Error: %s" % (path, exception))


def add_tarfile(tar, name, output):
    info = tarfile.TarInfo(name=name)
    info.size = output.tell()
    output.seek(0)
    tar.addfile(info, fileobj=output)


def export_db_dump(location):
    """Exports a full database dump to the specified location.
    Args:
        location: Directory where the archive will be created.
    Returns:
        Path to the created archive.
    """
    conn = psycopg2.connect(**current_app.config["PG_INFO"])
    create_path(location)
    time_now = datetime.today()

    archive_name = "mbspotify-dump-%s" % time_now.strftime("%Y%m%d-%H%M%S")
    archive_path = os.path.join(location, archive_name + ".tar.xz")

    with open(archive_path, "w") as archive:
        pxz_command = ["pxz", "--compress"]
        pxz = subprocess.Popen(pxz_command,
                               stdin=subprocess.PIPE,
                               stdout=archive)

        with tarfile.open(fileobj=pxz.stdin, mode="w|") as tar:
            output = io.StringIO(time_now.isoformat(" "))
            add_tarfile(tar, os.path.join(archive_name, "TIMESTAMP"), output)

            tar.add(DUMP_LICENSE_FILE_PATH,
                    arcname=os.path.join(archive_name, "COPYING"))

            cur = conn.cursor()
            for table_name in _TABLES:
                output = io.StringIO()
                print(" - Copying table %s..." % table_name)
                cur.copy_to(output, "(SELECT %s FROM %s)" %
                            (", ".join(_TABLES[table_name]), table_name))
                add_tarfile(tar,
                            os.path.join(archive_name, "dump", table_name),
                            output)

        pxz.stdin.close()
        pxz.wait()

    conn.close()
    return archive_path


def import_db_dump(archive_path):
    """Imports data from a .tar.xz archive into the database."""
    pxz_command = ["pxz", "--decompress", "--stdout", archive_path]
    pxz = subprocess.Popen(pxz_command, stdout=subprocess.PIPE)

    conn = psycopg2.connect(**current_app.config["PG_INFO"])
    try:
        cur = conn.cursor()

        with tarfile.open(fileobj=pxz.stdout, mode="r|") as tar:
            for member in tar:
                file_name = member.name.split("/")[-1]

                if file_name in _TABLES:
                    print(" - Importing data into %s table..." % file_name)
                    cur.copy_from(tar.extractfile(member), '"%s"' % file_name,
                                  columns=_TABLES[file_name])
        conn.commit()
    finally:
        conn.close()

    pxz.stdout.close()
    pxz.wait()
