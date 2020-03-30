import json
import requests
import shutil
import os
import logging
import argparse
import generate_kosh_files


def get_logger():
    # Gets or creates a logger
    logger = logging.getLogger(__name__)

    # set log level
    logger.setLevel(logging.INFO)

    # define file handler and set formatter
    file_handler = logging.FileHandler('update_freedict.log')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    # add file handler to logger
    logger.addHandler(file_handler)

    return logger


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


def get_local_freedict(local_freedict):
    with open(local_freedict, 'r') as local_json:
        parsed_local = json.load(local_json)
        local_dict = parse_freedict_json(parsed_local)
    return local_dict


def get_dict_from_upstream(path_to_local_files, upstream_freedict, dict_id):
    # download and decompress new XML files (.tar.xz)
    # get tar from freedict.org
    response = requests.get(upstream_freedict.get(dict_id).get('url'), stream=True)
    tardata = response.content
    tarname = os.path.join(path_to_local_files, "{}.tar.gz".format(dict_id))
    tarfile = open(tarname, "wb")
    tarfile.write(tardata)
    tarfile.close()
    # untar
    shutil.unpack_archive(tarname, extract_dir=path_to_local_files)
    # delete downloaded tar
    os.remove(tarname)


def init_download(upstream_freedict, path_to_local_files, logger):
    r = requests.get(upstream_freedict)
    upstream_freedict = parse_freedict_json(r.json())
    # create dir if does not exists
    os.makedirs(path_to_local_files, exist_ok=True)
    for dict_id, props in upstream_freedict.items():
        # get tar from freedict.org
        get_dict_from_upstream(path_to_local_files, upstream_freedict, dict_id)
        print(dict_id, 'downloaded and decompressed')
        # save a local copy of fredict-json
    with open('{}/freedict-database.json'.format(path_to_local_files), 'w') as f:
        json.dump(r.json(), f, indent=4)
        logger.info('Local copy of freedict downloaded at {}'.format(path_to_local_files))


def compare_and_download_new_dicts(local_freedict, upstream_freedict, path_to_local_files, logger):
    r = requests.get(upstream_freedict)
    upstream_freedict = parse_freedict_json(r.json())
    modified = False

    # check intersection of dict_ids
    for dict_id in local_freedict.keys() & upstream_freedict.keys():
        local_checksum = local_freedict.get(dict_id).get('checksum')
        upstream_cheksum = upstream_freedict.get(dict_id).get('checksum')

        if local_checksum != upstream_cheksum:
            modified = True
            get_dict_from_upstream(path_to_local_files, upstream_freedict, dict_id)
            logger.info('{} has been updated from upstream'.format(dict_id))

    ## check diff. we assume that new dictionaries are included and existing dictionaries are not removed from freedict.org
    for dict_id in upstream_freedict.keys() - local_freedict.keys():
        modified = True
        get_dict_from_upstream(path_to_local_files, upstream_freedict, dict_id)
        logger.info('{} has been downloaded from upstream'.format(dict_id))

        # generate kosh_files for this dictionary
        generate_kosh_files.generate_dot_kosh(path_to_local_files, dict_id)
        generate_kosh_files.generate_mapping(path_to_local_files, dict_id)
        logger.info('kosh files generated for {}'.format(dict_id))

    if modified:
        # replace local copy of fredict-json
        with open('{}/freedict-database.json'.format(path_to_local_files), 'w') as f:
            json.dump(r.json(), f, indent=4)
        logger.info('new freedict-database.json saved')


def main(args):
    # set logger
    logger = get_logger()

    freedict_url = 'https://freedict.org/freedict-database.json'

    if args.init:
        init_download(freedict_url, args.path_to_freedict, logger)
        generate_kosh_files.generate_all_kosh_files(args.path_to_freedict)
        logger.info('kosh files generated for all dicts')


    else:
        path_to_json_file = '{}/freedict-database.json'.format(args.path_to_freedict)
        local_freedict = get_local_freedict(path_to_json_file)
        compare_and_download_new_dicts(local_freedict, freedict_url,
                                       args.path_to_freedict, logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_freedict', help='path to freedicts files')
    parser.add_argument("--init", help="initial download from freedict.org",
                        action="store_true")
    args = parser.parse_args()

    main(args)
