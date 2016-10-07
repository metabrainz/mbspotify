from __future__ import print_function
import os
import click
import subprocess
import mbspotify
import mbspotify.db

SQL_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sql')
app = mbspotify.create_app()


def _run_psql(script,
              host=app.config["PG_INFO"]["host"],
              port=app.config["PG_INFO"]["port"],
              user=app.config["PG_INFO"]["user"],
              database=app.config["PG_INFO"]["database"]):
    script = os.path.join(SQL_DIR, script)
    command = ['psql', '-h', host,
                       '-p', str(port),
                       '-U', user,
                       '-d', database,
                       '-f', script]
    exit_code = subprocess.call(command)
    return exit_code


cli = click.Group()


@cli.command()
@click.option("--create-db", is_flag=True)
@click.option("--force", "-f", is_flag=True,
              help="Drop existing database and user.")
@click.argument("archive", type=click.Path(exists=True), required=False)
def init_db(archive, force, create_db):
    """Initializes the database and imports data if needed.

    The archive must be a .tar.xz produced by the dump command.
    """
    if create_db:

        if force:
            exit_code = _run_psql('drop_db.sql')
            if exit_code != 0:
                raise Exception('Failed to drop existing database and user! '
                                'Exit code: %i' % exit_code)

        print('Creating user and a database...')
        exit_code = _run_psql('create_db.sql')
        if exit_code != 0:
            raise Exception('Failed to create new database and user! '
                            'Exit code: %i' % exit_code)

    print('Creating tables...')
    _run_psql('create_tables.sql', user='mbspotify', database='mbspotify')

    if archive:
        print('Importing data...')
        mbspotify.db.import_db_dump(archive)
    else:
        print('Skipping data importing.')

    print("Done!")


@cli.command()
@click.option("--location", "-l", default=os.path.join("/", "data", "export"),
              show_default=True,
              help="Directory where dumps need to be created")
@click.pass_context
def dump(ctx, location):
    """Exports a full database dump to the specified location.
    """
    print("Creating full database dump...")
    path = mbspotify.db.export_db_dump(location)
    print("Done! Created:", path)


if __name__ == '__main__':
    cli()
