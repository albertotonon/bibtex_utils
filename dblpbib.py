import glob
import re
import sys

import requests

cite_re = re.compile('\\\\cite{([^}]+)}')
cite_split_re = re.compile('\\s*,\\s*')


def extract_cites(content):
    all_cite_keys = set()
    for cite_group in cite_re.findall(content):
        # groups like 'x,y,z' extracted from text like \cite{x,y,z}
        cites = cite_split_re.split(cite_group)
        all_cite_keys.update(cites)
    return all_cite_keys


if __name__ == '__main__':
    if len(sys.argv) != 3:
        # TODO: make a function
        print("Give me two parameters:",
              "the home of your LaTeX project"
              "and the name of the bibtex file you want me to generate")
        print(sys.argv[0], 'project_home', 'output_filename')
        sys.exit()
    project_home = sys.argv[1]
    output_filename = sys.argv[2]
    all_tex_files = glob.glob(project_home + '/**/*.tex', recursive=True)

    print('extract all dblp cite keys')
    all_dblp_citekeys = set()
    for tex_filename in all_tex_files:
        f = open(tex_filename, 'r', encoding='utf-8')
        content = f.read()
        f.close()
        dblp_citekeys = extract_cites(content)
        all_dblp_citekeys.update(dblp_citekeys)

    print('get bibtex entries from dblp')
    dblp_baseurl = 'http://dblp.uni-trier.de/rec/bib2/'
    fout = open(output_filename, 'w', encoding='utf-8')
    for cite_key in all_dblp_citekeys:
        # cite keys must start with "DBLP:"
        url = dblp_baseurl + cite_key[5:]
        r = requests.get(url)
        r.encoding = 'UTF-8'
        if r.status_code != 200:
            print('got problems with cite-key "{}"'.format(cite_key))
            continue
        bibtex_entry = r.text
        print(bibtex_entry, file=fout)
    fout.close()
