import sys

def write_percent_progress(progress: int, total: int) -> None:
    sys.stdout.write("\rCheckpoint {:.2f}%    ".format(100*progress/total))
    sys.stdout.flush()
    if progress == total:
        sys.stdout.write("\n\n")