import os, sys, tempfile
import PySide6.QtWidgets as qtw

# Hack to allow imports from src/ example: "src.algorithm.API"
# src: https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.append(parentdir)


from MainWindow.MainWindow import Window

# Directory for storing tempfiles. Automatically deletes on program exit.
ROOT_TEMP_DIRECTORY = tempfile.TemporaryDirectory(prefix="FocusStacking_")

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    window = Window(ROOT_TEMP_DIRECTORY)

    window.show()
    sys.exit(app.exec())

ROOT_TEMP_DIRECTORY.cleanup()
