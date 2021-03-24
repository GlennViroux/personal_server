from glob import glob
from pathlib import Path

TEMP_DIR = Path("./ffmpeg_temp_files")

def get_temp_file(filetype):
    base_dir = TEMP_DIR / filetype
    base_dir.mkdir(parents=True,exist_ok=True)
    current_files = sorted(glob(str(TEMP_DIR / filetype)+f"/*{filetype}"))
    numbers = [0]

    for f in current_files:
         numbers.append(int(str(f).split("/")[-1].split(".")[0].split("_")[-1]))

    result = TEMP_DIR / filetype / f"sample_{max(numbers)+1}.{filetype}"

    return result



