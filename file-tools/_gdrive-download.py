import argparse
from google_drive_downloader import GoogleDriveDownloader as gdd


def parse():
    ap = argparse.ArgumentParser("gdrive-download", add_help=True,
                                 description="Downloads a file from Google Drive from its shared reference URL or ID.")
    ap.add_argument("file_id", help="Google Drive sharable reference URL or ID.")
    ap.add_argument("destination", help="Path to output location.")
    ap.add_argument("-f", "--force", action="store_true", dest="overwrite",
                    help="Force re-download and overwrite existing file.")
    ap.add_argument("-u", "--unzip", action="store_true",
                    help="Unzip the downloaded file if applicable.")
    ap.add_argument("-v", "--verbose", dest="show", action="store_true",
                    help="Display downloaded file details.")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse()
    dest = args.destination
    if args.unzip and not dest.endswith(".zip"):
        dest = dest + ".zip"
        print(f"Updated destination: {dest}")
    gdd.download_file_from_google_drive(args.file_id, dest, args.overwrite, args.unzip, args.show)
