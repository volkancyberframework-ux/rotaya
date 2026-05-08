import os
import re
import shutil

# =========================
# AYARLAR
# =========================

TEMPLATES_DIR = "./core/templates"
IMAGES_DIR = "./core/static/assets/images"
UNUSED_DIR = "./unused_static/images"

IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
)

# =========================
# KULLANILAN DOSYALAR
# =========================

used_images = set()

print("\nHTML dosyalari taraniyor...\n")

# templates altındaki tüm html dosyalarını tara
for root, dirs, files in os.walk(TEMPLATES_DIR):

    for file in files:

        if file.endswith(".html"):

            html_path = os.path.join(root, file)

            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()

                    # images klasöründeki tüm dosyaları kontrol et
                    for img_root, _, img_files in os.walk(IMAGES_DIR):

                        for img in img_files:

                            if img.lower().endswith(IMAGE_EXTENSIONS):

                                # Dosya adı HTML içinde geçiyor mu?
                                if img in content:
                                    used_images.add(img)

            except Exception as e:
                print(f"HATA OKUMA: {html_path} -> {e}")

# =========================
# KULLANILMAYANLARI TAŞI
# =========================

print("\nKullanilmayan resimler tasiniyor...\n")

moved_count = 0

for root, dirs, files in os.walk(IMAGES_DIR):

    for file in files:

        if file.lower().endswith(IMAGE_EXTENSIONS):

            # kullanılmıyorsa taşı
            if file not in used_images:

                original_path = os.path.join(root, file)

                # klasör yapısını koru
                relative_path = os.path.relpath(
                    original_path,
                    IMAGES_DIR
                )

                destination_path = os.path.join(
                    UNUSED_DIR,
                    relative_path
                )

                os.makedirs(
                    os.path.dirname(destination_path),
                    exist_ok=True
                )

                try:
                    shutil.move(original_path, destination_path)

                    print(f"TASINDI: {original_path}")

                    moved_count += 1

                except Exception as e:
                    print(f"HATA TASIMA: {original_path} -> {e}")

print("\n===================================")
print(f"Toplam tasinan resim: {moved_count}")
print("===================================\n")
