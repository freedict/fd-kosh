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


def get_local_freedict(local_freedict):
    with open(local_freedict, 'r') as local_json:
        parsed_local = json.load(local_json)
        local_dict = parse_freedict_json(parsed_local)
    return local_dict


def get_dict_from_upstream(path_to_xml_files, path_to_source, upstream_freedict, dict_id):
    url = upstream_freedict.get(dict_id).get('url')
    local_path_to_upstream_dict = url.replace('https://download.freedict.org', path_to_source + '/download')
    tarname = local_path_to_upstream_dict
    # untar
    shutil.unpack_archive(tarname, extract_dir=path_to_xml_files)


def get_freedict_list_from_upstream(freedict_url):
    with open(freedict_url) as f:
        data = json.load(f)
    return data


def compare_and_download_new_dicts(local_freedict, path_to_source, path_to_xml_files, logger):
    path_to_up_to_date_db_file = path_to_source + '/freedict-database.json'
    upstream_freedict = parse_freedict_json(get_freedict_list_from_upstream(path_to_up_to_date_db_file))
    modified = False
    # check intersection of dict_ids
    for dict_id in local_freedict.keys() & upstream_freedict.keys():
        local_checksum = local_freedict.get(dict_id).get('checksum')
        upstream_checksum = upstream_freedict.get(dict_id).get('checksum')
        if local_checksum != upstream_checksum:
            modified = True
            get_dict_from_upstream(path_to_xml_files, path_to_source, upstream_freedict, dict_id)
            logger.info('{} has been updated from upstream'.format(dict_id))

    ## check diff. we assume that new dictionaries are included and existing dictionaries are not removed from freedict.org
    for dict_id in upstream_freedict.keys() - local_freedict.keys():
        modified = True
        get_dict_from_upstream(path_to_xml_files, path_to_source, upstream_freedict, dict_id)
        logger.info('{} has been downloaded from upstream'.format(dict_id))
        # generate kosh_files for this dictionary
        generate_kosh_files.generate_dot_kosh(path_to_xml_files, dict_id)
        generate_kosh_files.generate_mapping(path_to_xml_files, dict_id)
        logger.info('kosh files generated for {}'.format(dict_id))

    if modified:
        # replace local copy of fredict-json
        with open('{}/freedict-database.json'.format(path_to_xml_files), 'w') as f:
            json.dump(get_freedict_list_from_upstream(path_to_up_to_date_db_file), f, indent=4)
        logger.info('new freedict-database.json saved')


def init_download(path_to_source, path_to_xml_files, logger):
    path_to_up_to_date_db_file = path_to_source + '/freedict-database.json'
    upstream_freedict = parse_freedict_json(get_freedict_list_from_upstream(path_to_up_to_date_db_file))
    # create dir if does not exists
    os.makedirs(path_to_xml_files, exist_ok=True)
    for dict_id, props in upstream_freedict.items():
        # get tar from freedict.org
        get_dict_from_upstream(path_to_xml_files, path_to_source, upstream_freedict, dict_id)
        # save a local copy of fredict-json
    with open('{}/freedict-database.json'.format(path_to_xml_files), 'w') as f:
        json.dump(get_freedict_list_from_upstream(path_to_up_to_date_db_file), f, indent=4)
        logger.info('Local copy of freedict at {}'.format(path_to_xml_files))


def main(args):
    # set logger
    logger = get_logger()
    if args.init:
        init_download(args.path_to_source, args.path_to_xml_files, logger)
        generate_kosh_files.generate_all_kosh_files(args.path_to_xml_files)
        logger.info('kosh files generated for all dicts')
    else:
        path_to_current_db_file = '{}/freedict-database.json'.format(args.path_to_xml_files)
        local_freedict = get_local_freedict(path_to_current_db_file)
        compare_and_download_new_dicts(local_freedict, args.path_to_source,
                                       args.path_to_xml_files, logger)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_source', help='path_to_source')
    parser.add_argument('path_to_xml_files', help='path to freedict xml files')
    parser.add_argument("--init", help="initialize",
                        action="store_true")
    args = parser.parse_args()
    main(args)
