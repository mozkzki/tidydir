TARGET_EXTENSIONS_IMAGE = [
    ".jpg",
    ".JPG",
    ".jpeg",
    ".JPEG",
    ".png",
    ".PNG",
    "heic",
    "HEIC",
]
TARGET_EXTENSIONS_MOVIE = [".mp4", ".MP4", ".mov", ".MOV", ".mts", ".MTS"]
TARGET_EXTENSIONS = []
# TARGET_EXTENSIONS.extend(TARGET_EXTENSIONS_IMAGE)  # Imageは除外
TARGET_EXTENSIONS.extend(TARGET_EXTENSIONS_MOVIE)
