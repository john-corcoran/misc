#!/usr/bin/env python

"""Python 2.7 compatible creation of zip files for each file at given paths"""

import argparse
import os
import subprocess


def get_file_paths(paths, ignore_dotfiles):
    """Get list of file paths at a path (recurses subdirectories) and total size of directory"""
    files = []
    for path in sorted(paths):
        for root, dirs, filenames in os.walk(path):
            if ignore_dotfiles:
                filenames = [f for f in filenames if not f[0] == "."]
                dirs[:] = [d for d in dirs if not d[0] == "."]
            for name in filenames:
                files.append(os.path.join(root, name))
    return sorted(files)


def get_safe_path_name(path_name):
    """Return the provided file_name string with all non alphanumeric characters removed"""

    def safe_char(char):
        if char.isalnum():
            return char
        else:
            return "_"

    return "".join(safe_char(char) for char in path_name).rstrip("_")


def get_unused_output_path(file_path):
    """If a file already exists at path, get a similar new file path instead"""
    file_basename_noext = os.path.splitext(os.path.basename(file_path))[0]
    filename_suffix = 2
    while os.path.isfile(file_path):
        file_path = os.path.join(
            os.path.dirname(file_path),
            "{}_{}{}".format(
                file_basename_noext,
                filename_suffix,
                os.path.splitext(file_path)[1],
            ),
        )
        filename_suffix += 1
    return file_path


def get_missing_sources(source_paths, files_only=False):
    """Return list of any source paths that aren't a file or a folder"""
    missing_sources = [
        source_path
        for source_path in source_paths
        if (not os.path.isdir(source_path) or files_only) and not os.path.isfile(source_path)
    ]
    return missing_sources


def get_list_as_str(list_to_convert):
    """Convert list into comma separated string, with each element enclosed in single quotes"""
    return ", ".join(["'{}'".format(list_item) for list_item in list_to_convert])


def main():
    """Capture args via argparse and create compressed copies of files across input path(s)"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_paths", nargs="+", help="Folder(s) containing items to zip")
    parser.add_argument("output_path", help="Folder to output to")
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        help="Password to use for zip file encryption",
    )
    parser.add_argument(
        "-d",
        "--include-dotfiles",
        action="store_false",
        help="Flag to include dotfiles in items to compress",
    )
    args = parser.parse_args()

    # Check passed arguments and return if issues
    if get_missing_sources(args.input_paths):
        print(
            "Path(s) {} not found".format(get_list_as_str(get_missing_sources(args.input_paths))),
        )
        return

    # Create output path if it does not already exist
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    # Compress each file
    for path in args.input_paths:
        output_subfolder = args.output_path
        if len(args.input_paths) > 1:
            output_subfolder = os.path.join(args.output_path, get_safe_path_name(path))
        file_paths = get_file_paths([path], args.include_dotfiles)
        if file_paths:
            print("{} files to compress in '{}'".format(len(file_paths), path))
        else:
            print("'{}' is empty".format(path))
        for file_input_path in file_paths:
            file_relative_path = os.path.relpath(file_input_path, path)
            file_output_path = os.path.join(
                output_subfolder, "{}.zip".format(os.path.splitext(file_relative_path)[0])
            )
            if os.path.isfile(file_output_path):
                file_output_path_unused = get_unused_output_path(file_output_path)
                print(
                    "'{}' already exists in '{}' - will use output filename '{}' instead".format(
                        file_output_path, output_subfolder, file_output_path_unused
                    )
                )
                file_output_path = file_output_path_unused
            # Create output path folder if it does not already exist
            if not os.path.exists(os.path.dirname(file_output_path)):
                os.makedirs(os.path.dirname(file_output_path))
            args_for_7z = [
                "7z",
                "a",
                file_output_path,
                file_input_path,
            ]
            if args.password is not None:
                args_for_7z.append("-p{}".format(args.password))
            ret = subprocess.check_output(
                args_for_7z,
                stderr=subprocess.STDOUT,
            )
            print(ret)

    print("Script complete")


if __name__ == "__main__":
    # Entry point when running script directly
    main()
