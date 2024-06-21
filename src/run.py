import argparse
import os, sys, tempfile, glob
import pathlib
import PySide6.QtCore as qtc
import PySide6.QtWidgets as qtw
import PySide6.QtGui as qtg

# Allow imports from top level folder. Example: "src.algorithm.API"
# src: https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)  # Insert at first place

import src.settings as settings

DEFAULT_FILENAME = "stacked"
DEFAULT_FILETYPE = "jpg"
SUPPORTED_OUTPUT_FILETYPES = ["jpg", "jpeg", "png", "tif"]


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main_ui():
    import src.MainWindow as MainWindow

    # Directory for storing tempfiles. Automatically deletes on program exit.
    ROOT_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="ChimpStackr_")
    settings.globalVars["RootTempDir"] = ROOT_TEMP_DIRECTORY

    # Taskbar icon fix for Windows
    # Src: https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7S
    if os.name == "nt":
        import ctypes

        myappid = "test.application"  # arbitrary string
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass  # Platform older than Windows 7

    qApp = qtw.QApplication([])
    # Needed for saving QSettings
    qApp.setApplicationName("ChimpStackr")
    qApp.setOrganizationName("noah.peeters")
    # Uses names of QApplication (above)
    settings.globalVars["QSettings"] = qtc.QSettings()
    settings.globalVars["MainApplication"] = qApp

    # Get icon for Windows/Mac (PyInstaller) or source code run
    icon_path = resource_path("packaging/icons/icon_512x512.png")
    if not os.path.isfile(icon_path):
        # Path to icon inside AppImage
        icon_path = "icon_128x128.png"

    window = MainWindow.Window()

    icon = qtg.QIcon(icon_path)
    qApp.setWindowIcon(icon)

    window.showMaximized()
    qApp.exec()


def parse_args():
    parser = argparse.ArgumentParser(
        prog="ChimpStackr", description="Command line interface to ChimpStackr"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_FILENAME,
        help=f"Name of the output file including file extension. Defaults to {DEFAULT_FILENAME}.",
    )
    parser.add_argument(
        "files",
        type=str,
        nargs="+",
        help="List of input files to be stacked.",
    )
    parser.add_argument(
        "-f",
        "--filetype",
        type=str,
        default=DEFAULT_FILETYPE,
        help=f"If output file is not specified, this option sets the filetype of the default filename, currently supported are: {SUPPORTED_OUTPUT_FILETYPES}",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=None,
        help="Quality/compression factor for output file. 0-100 for JPG and 0-9 for PNG. Not supported for TIF files.",
    )

    parsed_args = parser.parse_args()
    if parsed_args.filetype not in SUPPORTED_OUTPUT_FILETYPES:
        error_str = f"Output filetype {parsed_args.filetype} not supported!"
        raise Exception(error_str)

    if not parsed_args.files:
        raise Exception(f"Please specify files to stack!")

    return parsed_args


def main_cmd_line():
    from src.utilities import save_image
    from src.algorithms.API import LaplacianPyramid

    args = parse_args()
    img_out_path = args.output
    if img_out_path == DEFAULT_FILENAME:
        input_path = pathlib.Path(args.files[0])
        input_path = input_path if input_path.is_dir() else input_path.parent
        filename = pathlib.Path(args.output + "." + args.filetype)
        img_out_path = (input_path / filename).as_posix()

    img_type = pathlib.Path(img_out_path).suffix.lstrip(".").lower()

    if len(args.files) == 1 and pathlib.Path(args.files[0]).is_dir():
        files = glob.glob(os.path.join(args.files[0], "*"))
    else:
        files = args.files

    stacker = LaplacianPyramid(use_pyqt=False)
    stacker.update_image_paths(files)
    stacked_frame = stacker.align_and_stack_images(None)
    error_msg = save_image(stacked_frame, img_type, img_out_path, args.quality)
    if error_msg:
        raise Exception(error_msg)


if __name__ == "__main__":
    settings.init()

    if len(sys.argv) > 1:
        main_cmd_line()
    else:
        main_ui()
