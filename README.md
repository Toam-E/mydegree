# mydegree-import-helper

A quick Python tool for importing your transcript from the SAP system into [mydegree.co.il](https://www.mydegree.co.il/) easily.

## 📦 How to use

1. Export your transcript as PDF from the SAP system.
2. Replace the file `תדפיס.pdf` in this folder with your own exported transcript.
3. Run `main.py`.
4. A new file called `courses.json` will be created.
5. Open [mydegree](https://www.mydegree.co.il/), click the three dots → "Import from JSON file", and paste the contents of `courses.json`.

## ✅ Notes

- Currently only supports Hebrew transcripts.
- A dedicated "קיץ פטורים" semester is created for all exempted/credited courses.
- Binary courses are handled automatically.

---

Made for friends who are too lazy to copy grades one by one 😄
