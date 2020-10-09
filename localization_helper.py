"""
CK3 Localization Helper script by erri120 under GPLv3.

Usage:

Updating translations:

python localization_helper.py update --lang german

Viewing statistics:

python localization_helper.py stats

Viewing statistics for a specific language:

python localization_helper.py stats --lang german

"""

import os;
import argparse;
import sys;
import glob;
import shutil;
from typing import Tuple, List;

#key, value, translated, comment
Yaml = Tuple[str, str, bool, bool];

BASE_LANGUAGE = 'english';
ENCODING = 'utf-8-sig';

localization_dir = os.path.abspath('localization');
base_dir = os.path.join(localization_dir, BASE_LANGUAGE);

def create_empty_list(count: int) -> List[str]:
    """Creates a new empty list"""
    return [''] * count;

def is_empty(string: str) -> bool:
    """Checks if the string is empty or only has whitespaces"""

    if not string:
        return True;
    return string.isspace();


def get_lang_name(lang: str) -> str:
    """Returns the name ending for a language."""

    return 'l_'+lang;

def get_yaml(string: str) -> Yaml:
    """Gets a YAML Tuple for the current line"""

    empty = ('', '', False, False);

    if is_empty(string):
        return empty;

    line = string.strip();
    comment_index = -1;

    try:
        comment_index = line.index('#');
        if comment_index == 0:
            return ('', '', False, True);
    except ValueError:
        pass;

    line_len = len(line);
    index = -1;
    key = '';
    value = '';
    translated = False;

    try:
        index = line.index(':');
    except ValueError:
        print('Unable to get index of : in line \"'+line+'\"');
        return empty;

    key = line[0:index];

    if line_len <= index+1:
        return (key, value, translated, False);

    if not is_empty(line[index+1]):
        translation_value = line[index+1];
        if not translation_value in ('0', '1'):
            print('Unknown translation value \"'+translation_value+'\" in line \"'+line+'\"');
        else:
            translated = translation_value == '1';
        value = line[index+2:].strip();
    else:
        value = line[index+1:].strip();

    result = (key, value, translated, False);
    return result;

def get_yaml_from_file(path: str) -> List[Yaml]:
    """Reads a file and returns a list of all YAML values"""

    yaml = list();
    with open(path, 'r', encoding=ENCODING) as file_stream:
        line = file_stream.readline();
        while line:
            yaml.append(get_yaml(line));
            line = file_stream.readline();

    return yaml;

def yaml_to_string(yaml: Yaml, include_translate: bool = True) -> str:
    """Converst a YAML Tuple to string"""
    translate_str = '' if not include_translate else '1' if yaml[2] else '0';
    return yaml[0]+':'+translate_str+' '+yaml[1]+'\n';

def update_translation_file(input_path: str, output_path: str, output_lang: str):
    """Updates the provided file with new translations"""

    output_lang_name = get_lang_name(output_lang);

    print('Updating file '+output_path);

    if not os.path.exists(output_path):
        print('File does not exist, copying from '+input_path+' to '+output_path);
        shutil.copyfile(input_path, output_path);

    input_yaml = get_yaml_from_file(input_path);
    output_yaml = get_yaml_from_file(output_path);

    input_len = len(input_yaml);
    output_len = len(output_yaml);
    new_lines = create_empty_list(input_len);

    if output_len != input_len:
        print('Input length does not equal output length: '+str(input_len)+'!='+str(output_len));

    for i in range(input_len):
        cur_input = input_yaml[i];
        # is comment
        if cur_input[3]:
            continue;

        if i == 0:
            new_lines[0] = output_lang_name+':\n';
            continue;

        if is_empty(cur_input[0]):
            new_lines[i] = '\n';
            continue;

        # searching for a YAML tuple with the same key as the current
        found_in_output = next((x for x in output_yaml if x[0] == cur_input[0]), ('', '', False));

        # not found means we just add the input
        if not found_in_output[0]:
            print('Missing key '+ cur_input[0]);
            new_lines[i] = yaml_to_string(cur_input);
            continue;

        # if we found it in the output file we check if it's translated
        if found_in_output[2]:
            new_lines[i] = yaml_to_string(found_in_output);
            continue;

        # if it's not translated then we copy the input
        new_lines[i] = yaml_to_string(cur_input);

    with open(output_path, 'w', encoding=ENCODING) as file_stream:
        file_stream.writelines(new_lines);


def copy_base_translations(input_dir: str, output_dir: str, input_lang: str, output_lang: str):
    """
    Recursively copies the contents of one folder to another and
    calls the updateFile function on every file.
    """

    input_lang_file_name = get_lang_name(input_lang)+'.yml';
    output_lang_file_name = get_lang_name(output_lang)+'.yml';

    if not os.path.exists(output_dir):
        os.mkdir(output_dir);
    items = glob.glob(input_dir + '/*');
    for item in items:
        if os.path.isdir(item):
            path = os.path.join(output_dir, item.split(os.path.sep)[-1]);
            copy_base_translations(item, path, input_lang, output_lang);
        else:
            file_name = item.split(os.path.sep)[-1];
            if file_name.endswith(input_lang_file_name):
                file_name = file_name.replace(input_lang_file_name, output_lang_file_name);
            path = os.path.join(output_dir, file_name);
            update_translation_file(item, path, output_lang);

def updating(output_language: str):
    """Updates all Translations"""

    print('Updating Translation for Language: '+output_language);
    output_dir = os.path.join(localization_dir, output_language);

    print('Using '+BASE_LANGUAGE+' Translations from '+base_dir+' in '+output_dir);
    copy_base_translations(base_dir, output_dir, BASE_LANGUAGE, output_language);

def get_translation_stats_file(base: str, path: str, cur_lang: str, detail: bool) -> Tuple[str, int, int]:
    """Gets the number of translated and not translated string of a file"""

    yaml = get_yaml_from_file(path);

    total = 0;
    translated = 0;
    not_translated = 0;

    lang_name = get_lang_name(cur_lang);

    for x in yaml:
        if x[3]:
            continue;
        if is_empty(x[0]):
            continue;
        if x[0] == lang_name:
            continue;

        total += 1;
        if x[2]:
            translated += 1;
        else:
            if detail:
                print(path+' '+x[0]);
            not_translated += 1;

    return (path.replace(base, ''), translated, not_translated);

def get_translation_stats_folder(base: str, folder: str, cur_lang: str, detail: bool) -> List[Tuple[str, int, int]]:
    """Gets Translation stats for a folder"""

    result = list();

    items = glob.glob(folder + '\\*');
    for item in items:
        if os.path.isdir(item):
            dir_stats = get_translation_stats_folder(base, item, cur_lang, detail);
            for stat in dir_stats:
                result.append(stat);
        else:
            file_stats = get_translation_stats_file(base, item, cur_lang, detail);
            result.append(file_stats);

    return result;

def add(enumerable: List[int]) -> int:
    """Adds all numbers of a list"""

    i = 0;
    for x in enumerable:
        i += x;
    return i;

def stats(lang: str):
    """Displays Translation Statistics"""

    print('Translation Statistics:\n');
    print('%-15s %10s %7s %7s' % ('Language ', 'Translated', 'Missing', 'Ratio'))

    languages = glob.glob(localization_dir+'\\*');
    detail = lang != '';
    for language in languages:
        name = language.replace(localization_dir+'\\', '');
        if name == BASE_LANGUAGE:
            continue;
        if detail and lang != name:
            continue;
        lang_stats = get_translation_stats_folder(language+'\\', language, name, detail);
        translated = list(map(lambda x: x[1], lang_stats));
        missing = list(map(lambda x: x[2], lang_stats));
        total_translated = add(translated);
        total_missing = add(missing);
        total = total_translated+total_missing;
        ratio = (total_translated/total)*100;

        ratio_str = f'{ratio:.2f}%';

        print('%-15s %10s %7s %7s' % (name, total_translated, total_missing, ratio_str))


def main():
    """Main"""
    parser = argparse.ArgumentParser('Localization Helper',
        description='Localization Helper by erri120',
        allow_abbrev=False);
    parser.add_argument('verb',
        help='Translation Update or Statistics',
        choices=('update', 'stats'));
    parser.add_argument('--lang',
        action='store',
        type=str,
        metavar='Language',
        help='Language for Translation Updates');
    args = parser.parse_args();

    lang = args.lang;
    if args.verb == 'update':
        if lang is None:
            print('update requires --lang to be set!');
            sys.exit(-1);
        updating(lang);
    else:
        if lang is None:
            stats('');
        else:
            stats(lang);

if __name__ == '__main__':
    main();
