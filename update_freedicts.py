import json
import requests
import shutil
import os
import sys
import logging


def parse_freedict_json(freedict_json):
    parsed_json_dict = {}
    for data_set in freedict_json:
        dict_id = data_set.get('name')
        releases = data_set.get('releases')
        if releases:
            for release in releases:
                platform = release.get('platform')
                checksum = release.get('checksum')
                url = release.get('URL')
                if platform == 'src':
                    parsed_json_dict[dict_id] = {}
                    parsed_json_dict[dict_id]['checksum'] = checksum
                    parsed_json_dict[dict_id]['url'] = url

    return parsed_json_dict


def compare_and_download_new_dicts(local_freedict, upstream_freedict, path_to_local_files, logger):
    r = requests.get(upstream_freedict)
    upstream_freedict = parse_freedict_json(r.json())

    for upstream_id, upstream_props in upstream_freedict.items():
        for local_id, local_props in local_freedict.items():
            if local_id == upstream_id:
                local_checksum = local_props.get('checksum')
                upstream_cheksum = upstream_props.get('checksum')
                if local_checksum != upstream_cheksum:
                    # download and decompress new XML files (.tar.xz)
                    path_to_decompress = path_to_local_files
                    os.makedirs(path_to_decompress, exist_ok=True)
                    # get tar from freedict.org
                    response = requests.get(upstream_props.get('url'), stream=True)
                    tardata = response.content
                    tarname = os.path.join(path_to_decompress, "{}.tar.gz".format(local_id))
                    tarfile = open(tarname, "wb")
                    tarfile.write(tardata)
                    tarfile.close()
                    # untar
                    shutil.unpack_archive(tarname, extract_dir=path_to_decompress)
                    # delete downloaded tar
                    os.remove(tarname)
                    logger.info('{} has been updated from upstream'.format(local_id))

    # replace local copy of fredict-json
    with open('{}/freedict-database.json'.format(path_to_local_files), 'w') as f:
        json.dump(r.json(), f, indent=4)
    logger.info('freedict-database.json has been updated')


def get_local_freedict(local_freedict):
    with open(local_freedict, 'r') as local_json:
        parsed_local = json.load(local_json)
        local_dict = parse_freedict_json(parsed_local)
    return local_dict


def create_logger(path_to_local_freedicts):
    # Gets or creates a logger
    logger = logging.getLogger(__name__)

    # set log level
    logger.setLevel(logging.INFO)

    # define file handler and set formatter
    file_handler = logging.FileHandler('freedicts-updates.log')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)

    return logger


def main():
    path_to_local_freedicts = sys.argv[1]  # e.g. /home/me/repos/freedict

    # set logger
    logger = create_logger(path_to_local_freedicts)

    path_to_json_file = '{}/freedict-database.json'.format(path_to_local_freedicts)
    local_freedict = get_local_freedict(path_to_json_file)
    compare_and_download_new_dicts(local_freedict, 'https://freedict.org/freedict-database.json',
                                   path_to_local_freedicts, logger)


if __name__ == "__main__":
    main()
