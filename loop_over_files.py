#!/usr/bin/env python

import os

def main():

    rootdir = '/home/dbauer/python_code/test'

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            if file.endswith(".txt"):
                print subdir+'/'+file
                fullpath=subdir+'/'+file
                with open(fullpath, "a") as myfile:
                    myfile.write("appended this \n")



if __name__ == '__main__':
    main()