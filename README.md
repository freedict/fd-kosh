Kosh API for FreeDict
==================

The Kosh API offers you the possibility to query FreeDict's dictionary entries
using a web API from within your programs.

This repository contains scripts that allow you to: 

- Download and maintain an up-to-date local version of the [freedict database](https://freedict.org/freedict-database.json).
- Automatically create files required by [Kosh](http://kosh.uni-koeln.de). Kosh is a framework for creating and maintaining APIs for Dictionaries.

Requirements: python3\
Optionally (if wanted): docker, docker-compose

Usage
-----
## HTTP Access
### Initialization

For downloading the complete freedict collection (more than 150 dictionaries,
April 2020) and creating Kosh files for each dictionary execute:

    python3 update_freedict.py /ABS_PATH_TO/fd-kosh_data --init

Where `/ABS_PATH_TO/fd-kosh_data` can be any directory where you want to download and decompress the data and save the Kosh files to. 
The directory will be created if not present.
After this, every subdirectory should look like this:

```
-rw-r--r--   1 me me 1375438 Mai 21  2019 afr-deu.tei
-rw-r--r--   1 me me     106 Mär 10  2019 AUTHORS
-rw-r--r--   1 me me     307 Mär 10  2019 ChangeLog
-rw-r--r--   1 me me   17982 Mär 10  2019 COPYING
-rw-r--r--   1 me me    4783 Mär 10  2019 freedict-dictionary.css
-rw-r--r--   1 me me  159913 Mär 10  2019 freedict-P5.dtd
-rw-r--r--   1 me me  406817 Mär 10  2019 freedict-P5.rng
-rw-r--r--   1 me me   17450 Mär 10  2019 freedict-P5.xml
-rw-r--r--   1 me me    4560 Mär 10  2019 INSTALL
-rw-rw-r--   1 me me      67 Mär 31 14:59 .kosh
-rw-rw-r--   1 me me     534 Mär 31 14:59 kosh_afr-deu_mapping.json
-rw-r--r--   1 me me     664 Mär 10  2019 Makefile
-rw-r--r--   1 me me       0 Mär 10  2019 NEWS
-rw-r--r--   1 me me     104 Mär 10  2019 README
```

`.kosh` and `kosh_DATASET_ID_mapping.json` are required by Kosh to create APIs for each dataset.

In `/ABS_PATH_TO/fd-kosh_data` you should find a copy of the freedict database: `freedict-database.json`

### Updating the Dictionary Database

`update_freedict.py` compares the local and upstream checksums of each dictionary. 
To check for updates you only need to execute the almost the command as when you are downloading the freedicts for the first time. 
The only difference here is that you do not have to add the `--init` option.

    python3 update_freedict.py /ABS_PATH_TO/fd-kosh_data

#### Automatic updates

Updates of the FreeDict database can be checked automatically with a 
Cronjob. The Cron job can be created as follows:

1. `crontab -e` to open the Cron configuration in your editor.
2. To check for updates daily at 23:00: 

    ```
    # For more information see the manual pages of crontab(5) and cron(8)
    # m h  dom mon dow   command
    00 23 * * * cd /ABS_PATH_TO/fd-kosh && /usr/bin/python3 /ABS_PATH_TO/fd-kosh/update_freedict.py /ABS_PATH_TO/fd-kosh_data
    ```
3.  In the log file `fd-kosh/update_freedict.log` you will see which datasets have been updated.

### Create APIs with Kosh

Kosh allows you to create and maintain APIs for Dictionaries. 
For each freedict Kosh builds two APIs: a RESTful and a GraphQL API.
Each API can be tested via a dedicated UI: a Swagger UI for each REST API and GraphiQL for each GraphQL API.

1.  Download Kosh

        git clone https://github.com/cceh/kosh.git
        
2.  Deploy Kosh

    Kosh requires elasticsearch. In order to avoid downloading and installing
    elasticsearch and Java yourself, we recommend you to deploy Kosh with
    Docker. Therefore it is recommended to install
    [Docker](https://docs.docker.com/install/) and
    [Docker-Compose](https://docs.docker.com/compose/install/), e.g. through
    `sudo apt install docker docker-compose`.
    In `docker-compose.local.yml`, you need to provide the path to your local
    copy of the FreeDict Kosh data:

        volumes: ['/ABS_PATH_TO/fd-kosh_data:/var/lib/kosh:ro']

    Keep in mind that indexing more than 150 datasets will not be a fast task.
    For testing purposes, first deploy only a single dataset:

        volumes: ['/ABS_PATH_TO/fd-kosh_data/afr-deu:/var/lib/kosh:ro']

    Then execute:

        (sudo) docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

    The `-d` means detached. To look at Kosh's logs, execute:

        (sudo) docker-compose -f docker-compose.yml -f docker-compose.local.yml logs

    After you see a message like this one in the logs:

        kosh_1     | 2020-03-26 14:51:35 [INFO] <kosh.kosh> Deploying web server at 0.0.0.0:5000

3.  Querying the freedict collection
    1.  REST APIs

        You can access a Swagger UI for each dataset on your computer/server: `http://localhost:5000/api/DATASET_ID/restful`

        IMPORTANT: The URL for each DATASET_ID in Kosh has an underscore instead of a dash.
        For example: `http://localhost:5000/api/lat_eng/restful`

        If you want to search for all the Latin headwords that start with 'aba'. Make a 'prefix' query. The query's URL should look like this:\
        `http://localhost:5000/api/lat_eng/restful/entries?field=headword&query=aba&query_type=prefix`
    2.  GraphQL APIs

        You can access a Swagger UI for each dataset on your computer/server: `http://localhost:5000/api/DATASET_ID/graphql`\
        For example: `http://localhost:5000/api/deu_nld/graphql`

        If you want to search for the meaning of the headword 'lieben' in Dutch, type on the left pane:

    ```
    {
      entries(queryType: term, query: "lieben", field: headword) {
        translation
      }
    }
    
    ```

4. Updating Kosh

    Per default Kosh updates a dataset's index if a related file has been
    modified. Therefore, if you automatically update the freedict collection
    with `fd-kosh`, Kosh will automatically update the respective index. 
    
    
    
## Local Access

When deploying Kosh within the freedict infrastructure there are a couple of modifications to be done to the above described steps.

### Initialization

For decompressing the XML files and generating the Kosh files, add the `--local` option:

`python3 update_freedict.py /ABS_PATH_TO/fd-kosh_data --init --local`

### Automatically updating and decompressing the XML files if freedict-database.json is modified

At `fd-kosh/path_unit_files` you will find `freedict_sync.service` and `freedict_sync.path`. 
Modify paths if required and add both files to `/etc/systemd/system/`
Then execute:
```
sudo systemctl enable freedict_sync.{path,service}
sudo systemctl start freedict_sync.path
```

 
### Bugs, Questions?

For more information about Kosh, please visit <https://kosh.uni-koeln.de>. If
you have found a bug in `fd-kosh`, please write an issue. Feel free to write to
our public 
You can also contact our
[public mailing list](https://www.freelists.org/list/freedict) or the author via
email: `f.mondaca [at] uni-koeln [dot] de`
