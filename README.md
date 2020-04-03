# fd-kosh   

This repository contains scripts that allow you to: 
- Download and maintain an up-to-date local version of the [freedict database](https://freedict.org/freedict-database.json).
- Automatically create files required by [Kosh](http://kosh.uni-koeln.de). Kosh is a framework for creating and maintaining APIs for Dictionaries.

Requirements: python3

## Usage:

### Initialization

For downloading the complete freedict collection (currently 149 dictionaries (31 March 2020)) and creating Kosh files 
for each dictionary execute:

`bash update_freedict.sh /ABS_PATH_TO/fd-kosh_data`

Where `/ABS_PATH_TO/fd-kosh_data` can be any directory where you want to download the data and save the Kosh files.

Is not mandatory to create the directory in advance. It can be empty too.

After this procedure every subdirectory should look like this:

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

### Update

`update_freedict.py` compares the local and upstream checksums of each dictionary. 
To check for updates you only need to execute the same command as when you are downloading the freedicts for the first time:

`bash update_freedict.sh /ABS_PATH_TO/fd-kosh_data`

In order to automatically check for updates, in Unix-like systems you could create a `cron` job:

1. `crontab -e`
2. For checking for updates daily at 23:00: 
```
# For more information see the manual pages of crontab(5) and cron(8)
#
# m h  dom mon dow   command
00 23 * * * bash /ABS_PATH_TO/fd-watch/update_freedict.sh /ABS_PATH_TO/fd-kosh_data

```

In the log file `fd-watch/update_freedict.log` you will see which datasets have been updated.

### Create APIs with Kosh

Kosh allows you to create and maintain APIs for Dictionaries. 
For each freedict (total: 149), Kosh will create 2 APIs: a RESTful and a GraphQL API.
Each API can be tested via a dedicated UI: a Swagger UI for each REST API and GraphiQL for each GraphQL API.

##### 1. Download Kosh

`git clone https://github.com/cceh/kosh.git`

##### 2. Deploy Kosh

Kosh requires elasticsearch. In order to avoid downloading and installing elasticsearch and Java yourself, we recommend you to
deploy Kosh with Docker. Therefore it is recommended to install [Docker](https://docs.docker.com/install/) and [Docker-Compose](https://docs.docker.com/compose/install/)

You need to provide in `docker-compose.local.yml` the path to your local copy of the freedict:

`volumes: ['/ABS_PATH_TO/fd-kosh_data:/var/lib/kosh:ro']`

Keep in mind that indexing 149 datasets will not be a fast task. For testing purposes, first deploy only a single dataset:

`volumes: ['/ABS_PATH_TO/fd-kosh_data/afr-deu:/var/lib/kosh:ro']`

Then execute:

`(sudo) docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d`

The `-d` means detached. To look at Kosh's logs, execute:

`(sudo) docker-compose -f docker-compose.yml -f docker-compose.local.yml logs`

After you see a message like this one in the logs:

`kosh_1     | 2020-03-26 14:51:35 [INFO] <kosh.kosh> Deploying web server at 0.0.0.0:5000`

You can test your Kosh instance.

##### 3. Querying the freedict collection

###### 3.1 REST APIs

You can access a Swagger UI for each dataset on your computer/server: `http://localhost:5000/api/DATASET_ID/restful`
IMPORTANT: The URL for each DATASET_ID in Kosh has an underscore instead of a dash.

For example: `http://localhost:5000/api/lat_eng/restful`

If you want to search for all the Latin headwords that start with 'aba'. Make a 'prefix' query. The query's URL should look like this:
`http://localhost:5000/api/lat_eng/restful/entries?field=headword&query=aba&query_type=prefix`

###### 3.2 GraphQL APIs

You can access a Swagger UI for each dataset on your computer/server: `http://localhost:5000/api/DATASET_ID/graphql`

For example: `http://localhost:5000/api/deu_nld/graphql`

If you want to search for the meaning of the headword 'lieben' in Dutch, type on the left pane:

```
{
  entries(queryType: term, query: "lieben", field: headword) {
    translation
  }
}

```
##### 4. Updating Kosh

Per default Kosh updates a dataset's index if a related file has been modified. Therefore, if you automatically update 
the freedict collection with `fd-watch`, Kosh will automatically update the respective index.
 
 
### Bugs, Questions?
For more information about Kosh, please visit https://kosh.uni-koeln.de. If you have found a bug in `fd-watch`, please, write an issue. You can also contact me via email: f.mondaca[at]uni-koeln.de




 

