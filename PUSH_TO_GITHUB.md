# Panduan Push ke GitHub (Step by Step)

Panduan ini khusus untuk mengunggah **Aldy Converter** ke GitHub dengan aman, tanpa file besar/sensitif ikut terbawa.

> Jalankan semua perintah dari dalam folder proyek: `D:\Aldy\aldy_converter`

---

## Langkah 0 — Pastikan Git terpasang

```bash
git --version
```
Jika belum ada, install dari https://git-scm.com/download/win lalu tutup & buka ulang terminal.

(Pertama kali pakai Git, set identitas — cukup sekali per komputer)
```bash
git config --global user.name "Nama Anda"
git config --global user.email "aldy.sidabutar@intramedika.co.id"
```

---

## Langkah 1 — Inisialisasi repository

```bash
git init
```

---

## Langkah 2 — Tambahkan semua file (menghormati .gitignore)

File `.gitignore` sudah disiapkan, jadi folder binari besar otomatis dikecualikan.

```bash
git add .
```

---

## Langkah 3 — ⚠️ VERIFIKASI (langkah paling penting!)

Cek file apa saja yang akan di-commit:

```bash
git status
```

**Pastikan TIDAK ada** baris berikut dalam daftar:
- `assets/ghostscript/`
- `assets/tesseract/`
- `tessdata/`
- `__pycache__/`
- `.mypy_cache/`

Jika folder di atas **tetap muncul**, JANGAN lanjut commit. Berhenti dan periksa lagi file `.gitignore`.

Untuk memastikan tidak ada file >50 MB yang ikut:
```bash
git ls-files | xargs -I{} du -h "{}" 2>/dev/null | sort -rh | head -10
```
Semua hasil harus berukuran kecil (KB, bukan MB besar).

---

## Langkah 4 — Commit pertama

```bash
git commit -m "Initial commit: Aldy Converter"
```

---

## Langkah 5 — Buat repository kosong di GitHub

1. Buka https://github.com/new
2. Isi **Repository name**, misalnya `aldy-converter`
3. Pilih **Private** (disarankan) atau Public
4. **JANGAN** centang "Add a README / .gitignore / license" (karena sudah ada di lokal)
5. Klik **Create repository**
6. Salin URL repo, contoh: `https://github.com/username/aldy-converter.git`

---

## Langkah 6 — Hubungkan & push

```bash
git branch -M main
git remote add origin https://github.com/username/aldy-converter.git
git push -u origin main
```

Saat diminta login, gunakan **Personal Access Token** sebagai password (bukan password akun GitHub):
- Buat token di: https://github.com/settings/tokens → "Generate new token (classic)" → centang scope `repo`.

---

## Selesai 🎉

Buka halaman repo Anda di GitHub dan pastikan README tampil dengan benar, serta folder `assets/` & `tessdata/` **tidak** ada di sana.

---

## Update berikutnya (setelah ada perubahan kode)

```bash
git add .
git status                       # cek lagi
git commit -m "Deskripsi perubahan"
git push
```

---

## Troubleshooting

| Masalah | Solusi |
|---|---|
| File besar terlanjur ke-`add` | `git rm -r --cached assets tessdata` lalu commit ulang |
| `remote origin already exists` | `git remote set-url origin <url-baru>` |
| Ditolak karena file >100 MB | Pastikan `.gitignore` benar; jika sudah terlanjur ter-commit, perlu hapus dari history (`git filter-repo`) |
| Diminta password terus | Gunakan Personal Access Token, atau install GitHub CLI (`gh auth login`) |
