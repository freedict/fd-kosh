import json
import urllib.request
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


def get_decompressed_freedict(local_freedict):
    with open(local_freedict, 'r') as local_json:
        parsed_local = json.load(local_json)
        local_dict = parse_freedict_json(parsed_local)
    return local_dict


def get_dict_from_upstream(path_to_xml_files, upstream_freedict, dict_id, local):
    tarname = os.path.join(path_to_xml_files, "{}.tar.gz".format(dict_id))
    dict_url = upstream_freedict.get(dict_id).get('url')
    if local:
        dict_url = dict_url.replace('https://download.freedict.org/', 'file:///var/www/download/')
    tardata, headers = urllib.request.urlretrieve(dict_url, tarname)
    # untar
    shutil.unpack_archive(tardata, extract_dir=path_to_xml_files)
    os.remove(tarname)


def get_freedict_list_from_upstream(freedict_url):
    res = urllib.request.urlopen(freedict_url)
    res_body = res.read()
    j = json.loads(res_body.decode("utf-8"))
    return j


def init_download(freedict_url, path_to_xml_files, logger, local):
    parsed_freedict_file = parse_freedict_json(get_freedict_list_from_upstream(freedict_url))
    # create dir if does not exists
    os.makedirs(path_to_xml_files, exist_ok=True)
    for dict_id, props in parsed_freedict_file.items():
        # get tar from freedict.org
        get_dict_from_upstream(path_to_xml_files, parsed_freedict_file, dict_id, local)
        print(dict_id, 'downloaded and decompressed')
        # save a local copy of fredict-json
    with open('{}/freedict-database.json'.format(path_to_xml_files), 'w') as f:
        json.dump(get_freedict_list_from_upstream(freedict_url), f, indent=4)
        logger.info('Local copy of freedict at {}'.format(path_to_xml_files))


def compare_and_download_new_dicts(local_freedict, freedict_url, path_to_xml_files, logger, local):
    upstream_freedict = parse_freedict_json(get_freedict_list_from_upstream(freedict_url))
    modified = False
    # check intersection of dict_ids
    for dict_id in local_freedict.keys() & upstream_freedict.keys():
        local_checksum = local_freedict.get(dict_id).get('checksum')
        upstream_cheksum = upstream_freedict.get(dict_id).get('checksum')
        if local_checksum != upstream_cheksum:
            modified = True
            get_dict_from_upstream(path_to_xml_files, upstream_freedict, dict_id, local)
            logger.info('{} has been updated'.format(dict_id))

    ## check diff. we assume that new dictionaries are added and existing dictionaries are not removed from freedict.org
    for dict_id in upstream_freedict.keys() - local_freedict.keys():
        modified = True
        get_dict_from_upstream(path_to_xml_files, upstream_freedict, dict_id, local)
        logger.info('{} has been downloaded from upstream'.format(dict_id))
        # generate kosh_files for this dictionary
        generate_kosh_files.generate_dot_kosh(path_to_xml_files, dict_id)
        generate_kosh_files.generate_mapping(path_to_xml_files, dict_id)
        logger.info('kosh files generated for {}'.format(dict_id))

    if modified:
        # replace local copy of fredict-json
        with open('{}/freedict-database.json'.format(path_to_xml_files), 'w') as f:
            json.dump(get_freedict_list_from_upstream(freedict_url), f, indent=4)
        logger.info('up-to-date freedict-database.json downloaded')


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {'false', 'f', '0', 'no', 'n'}:
        return False
    elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
        return True
    raise ValueError(f'{value} is not a valid boolean value')


def main(args):
    # set logger
    logger = get_logger()

    if args.local:
        freedict_url = 'file:///var/www/freedict-database.json'
        local = True
    else:
        freedict_url = 'https://freedict.org/freedict-database.json'
        local = False

    if args.init:
        init_download(freedict_url, args.path_to_xml_files, logger, local)
        print(freedict_url)
        generate_kosh_files.generate_all_kosh_files(args.path_to_xml_files)
        logger.info('kosh files generated for all dicts')
    else:
        downloaded_freedict_list = '{}/freedict-database.json'.format(args.path_to_xml_files)
        decompressed_freedict = get_decompressed_freedict(downloaded_freedict_list)
        compare_and_download_new_dicts(decompressed_freedict, freedict_url,
                                       args.path_to_xml_files, logger, local)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_xml_files',
                        help='path to freedict xml files that will be created if does not exists yet')
    parser.add_argument("--init", help="initial download from freedict.org",
                        action="store_true")
    parser.add_argument('--local', help='implementation at the freedict infrastructure', type=str_to_bool,
                        nargs='?', const=True, default=False)

    args = parser.parse_args()
    main(args)
