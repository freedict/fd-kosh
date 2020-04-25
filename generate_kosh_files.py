import os
import json
import argparse


def generate_dot_kosh(path_to_freedict, item):
    filename = "{}/{}/.kosh".format(path_to_freedict, item)
    with open(filename, mode="w") as writer:
        # [acc]
        writer.write('[{}]'.format(item.replace('-', '_')))
        writer.write('\n')
        # the only exception is eng-pol where all the entries are located in different XML files ([a..z].xml)
        if item == 'eng-pol':
            # list all the files in curr_dir
            list_of_xml_files = sorted(os.listdir(os.path.join(path_to_freedict, item, 'letters')))
            list_of_xml_files = ['letters/' + x for x in list_of_xml_files]
            writer.write('files: {}'.format(json.dumps(list_of_xml_files)))
            writer.write('\n')
        else:
            writer.write('files: ["{}.tei"]'.format(item))
            writer.write('\n')
        # schema: kosh_dict_mapping.json
        # abs_path_to_gen_dict_kosh_files = '{}/{}/'.format(abs_path_to_gen_kosh_files, dict)
        writer.write('schema: kosh_{}_mapping.json'.format(item))
        writer.write("\n")


def generate_mapping(path_to_freedicts, item):
    mappings = {}
    mappings['mappings'] = {}

    xpaths = {}
    xpaths['_xpaths'] = {}
    ## add objects to xpaths

    xpaths['_xpaths']['root'] = '//tei:entry'

    xpaths['_xpaths']['id'] = 'None'
    # fields to be indexed.
    # Kosh per default indexes the whole xml entry. NOTE: xml tags and attrs are not indexed.
    fields = {}
    fields['headword'] = './tei:form/tei:orth'
    fields['[translation]'] = ".//tei:sense/tei:cit[@type='trans']/tei:quote"
    xpaths['_xpaths']['fields'] = fields

    mappings['mappings']['_meta'] = xpaths

    properties = {}
    properties['headword'] = {}
    properties['headword']['type'] = 'keyword'
    properties['translation'] = {}
    properties['translation']['type'] = 'text'

    mappings['mappings']['properties'] = properties

    ## The 'properties' object provides elastic search with info for manipulating the index
    # strings classified as 'keyword' will not be analyzed i.e. they will not be tokenized or lowercased.
    # strings classified as 'text' will be analyzed

    with open('{}/{}/kosh_{}_mapping.json'.format(path_to_freedicts, item, item), 'w') as outfile:
        json.dump(mappings, outfile, indent=4)


def generate_all_kosh_files(path_to_xml_files):
    for item in os.listdir(path_to_xml_files):
        if os.path.isdir(os.path.join(path_to_xml_files, item)):
            # we create a .kosh file for each dict
            generate_dot_kosh(path_to_xml_files, item)
            generate_mapping(path_to_xml_files, item)


def main(args):
    path_to_xml_files = args.path_to_xml_files
    generate_all_kosh_files(path_to_xml_files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path_to_xml_files', help='path_to_xml_files')
    args = parser.parse_args()
    main(args)
