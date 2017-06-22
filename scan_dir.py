import os, re, csv, sys
import collections
import string


def get_list_files(dir1):
    Files = []
    i = 0
    for filename in os.listdir(dir1):
        if filename.endswith('.html'):
            dict1 = {
                'num': str(i),
                'name': filename
                }
            Files.append(dict1)
            i = i + 1
    return Files

def print_to_csv(Files, dir2):
    keys = ['num', 'name']
    with open(os.path.join(dir2,'filenames.csv'), 'w', newline='', encoding ='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, keys)
        writer.writeheader()
        writer.writerows(Files)
        csvfile.close()
    return
##########################

dir1 = "" #DIRECTORY OF FILES
dir2 = "" #LOCATION TO PUT OUTPUT


Files = get_list_files(dir1)
print_to_csv(Files, dir2)

