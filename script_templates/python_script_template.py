#!/usr/bin/env python3

"""[docstring]"""

import argparse
import datetime
import logging
import os
import pathlib
import platform
import typing


class MsgCounterHandler(logging.Handler):
    """Custom logging handler to count number of calls per log level"""

    def __init__(self, *args, **kwargs) -> None:
        super(MsgCounterHandler, self).__init__(*args, **kwargs)
        self.count = {}
        self.count["WARNING"] = 0
        self.count["ERROR"] = 0

    def emit(self, record) -> None:
        levelname = record.levelname
        if levelname not in self.count:
            self.count[levelname] = 0
        self.count[levelname] += 1


def _prepare_logging(
    datetime_string: str,
    write_logs: bool,
    folder_path: typing.Optional[str],
    identifier: str,
    args: typing.Dict[str, typing.Any],
    show_debug: bool = False,
    write_debug: bool = False,
) -> typing.Tuple[logging.Logger, MsgCounterHandler]:
    """Prepare and return logging object to be used throughout script"""
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    # 'Quiet' logger for when quiet flag used in functions
    quiet = logging.getLogger("quiet")
    quiet.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    if (write_logs or write_debug) and folder_path is not None:
        info_log = logging.FileHandler(
            os.path.join(folder_path, "{}_{}_info.log".format(datetime_string, identifier))
        )
        info_log.setLevel(logging.INFO)
        info_log.setFormatter(formatter)
        log.addHandler(info_log)
    if write_debug and folder_path is not None:
        debug_log = logging.FileHandler(
            os.path.join(folder_path, "{}_{}_debug.log".format(datetime_string, identifier))
        )
        debug_log.setLevel(logging.DEBUG)
        debug_log.setFormatter(formatter)
        log.addHandler(debug_log)
    console_handler = logging.StreamHandler()
    if show_debug:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)
    counter_handler = MsgCounterHandler()
    log.addHandler(counter_handler)
    # Log platform details and commandline arguments
    platform_detail_requests = [
        "python_version",
        "system",
        "machine",
        "platform",
        "version",
        "mac_ver",
    ]
    for platform_detail_request in platform_detail_requests:
        try:
            log.debug(
                "%s: %s", platform_detail_request, getattr(platform, platform_detail_request)()
            )
        except:  # pylint: disable=W0702
            pass
    log.debug("commandline_args: %s", args)
    return log, counter_handler


def main() -> None:
    """Captures args via argparse and [add functionality]"""
    script_filename = os.path.splitext(os.path.basename(__file__))[0]
    run_time = datetime.datetime.now()
    datetime_string = run_time.strftime("%Y%m%d_%H%M%S")

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        help=(
            "Write log files (will be written to folder '{}_logs' if alternate path not specified"
            " with --logfolder)".format(script_filename)
        ),
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Show debug log entries in console and write to separate log file in log folder",
    )
    parser.add_argument(
        "--logfolder",
        default="{}_logs".format(script_filename),
        help=(
            "Folder to write logs to (if not specified, folder '{}_logs' will be used in"
            " same directory as this script)".format(script_filename)
        ),
    )

    args = parser.parse_args()

    # Set up logging
    if args.log or args.debug:
        pathlib.Path(args.logfolder).mkdir(parents=True, exist_ok=True)
    log, counter_handler = _prepare_logging(
        datetime_string=datetime_string,
        write_logs=args.log,
        folder_path=args.logfolder,
        identifier=script_filename,
        args=dict(vars(args)),
        show_debug=args.debug,
        write_debug=args.debug,
    )
    if args.log:
        log.info("Logs will be stored in folder '%s'", args.logfolder)

    # Do stuff here

    # Mention any errors and close out
    if counter_handler.count["WARNING"] > 0 or counter_handler.count["ERROR"] > 0:
        log.warning(
            "Script complete; %s warnings/errors occurred requiring review - see log entries"
            " above%s",
            counter_handler.count["WARNING"] + counter_handler.count["ERROR"],
            (", replicated in folder '%s'", args.logfolder) if args.log or args.debug else "",
        )
    else:
        log.info("Script complete; no errors reported")


if __name__ == "__main__":
    # Entry point when running script directly
    main()
