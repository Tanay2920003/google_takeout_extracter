import zipfile
from pathlib import Path

# Source folder containing all takeout zip files
SOURCE_DIR = Path(r"C:\Users\tanay\Desktop\Data")

# Target extraction destination on D drive
EXTRACT_DIR = Path(r"D:\files\tanayanandmishra1")

def extract_takeout():
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort files numerically so extraction happens in order
    zip_files = sorted(list(SOURCE_DIR.glob("takeout-*.zip")))

    if not zip_files:
        print("No zip files found.")
        return

    print(f"Found {len(zip_files)} zip files. Starting extraction...\n")

    for index, zip_path in enumerate(zip_files, start=1):
        print(f"[{index}/{len(zip_files)}] Extracting {zip_path.name}...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
            print(f"✓ Extracted: {zip_path.name}")
        except zipfile.BadZipFile:
            print(f"❌ Error: {zip_path.name} is corrupted or incomplete.")
        except Exception as e:
            print(f"❌ Error extracting {zip_path.name}: {e}")

    print("\nExtraction complete! All files merged into:", EXTRACT_DIR.resolve())

if __name__ == "__main__":
    extract_takeout()