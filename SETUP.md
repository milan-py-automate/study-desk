# Study Desk — Vercel + Google Sheet Setup

## Step 1: Google Sheet banao
1. Google Sheets pe jaakar ek nayi sheet banao — naam kuch bhi rakho (jaise "Study Desk DB").
2. Isme kuch bharne ki zaroorat nahi — app khud "Materials" tab aur headers bana lega pehli baar chalne pe.
3. Sheet ke URL se **Sheet ID** copy karo:
   `https://docs.google.com/spreadsheets/d/`**`YEH_WALA_ID`**`/edit`

## Step 2: Google Service Account banao (backend ko sheet access dene ke liye)
1. https://console.cloud.google.com pe jao, naya project banao (ya purana use karo).
2. **APIs & Services → Library** me jaakar **Google Sheets API** enable karo.
3. **APIs & Services → Credentials → Create Credentials → Service Account** — naam kuch bhi do.
4. Service account bann jaane ke baad, usme jaakar **Keys → Add Key → Create New Key → JSON** choose karo — ek `.json` file download hogi. Yahi tumhara `GOOGLE_SERVICE_ACCOUNT_JSON` hai.
5. Us JSON file ke andar `"client_email"` field me ek email jaisa kuch dikhega (jaise `xxx@xxx.iam.gserviceaccount.com`).
6. Apni Google Sheet (Step 1) me **Share** button dabao, aur ye wala email **Editor** access ke saath add karo. (Ye sabse zaroori step hai — bina isके backend sheet ko chhoo nahi payega.)

## Step 3: Vercel pe deploy karo
1. Is poore folder (`app.py`, `index.html`, `vercel.json`, `requirements.txt`) ko ek GitHub repo me daalo.
2. https://vercel.com pe jaakar us repo ko import karo.
3. Deploy se pehle, **Environment Variables** me ye do add karo:
   - `SHEET_ID` → Step 1 wala Sheet ID
   - `GOOGLE_SERVICE_ACCOUNT_JSON` → Step 2 wali `.json` file ka **poora content** (ek hi line me paste kar sakte ho, JSON string ki tarah)
4. **Deploy** dabao. 1-2 minute me live link mil jayega (jaise `study-desk.vercel.app`).

## Use kaise karoge
- App khulte hi Sheet se data fetch hoga.
- "+ Naya subject jodo" → subject banega → chapter jodo → us chapter ke andar PDF/Video/Audio/Slide me se koi bhi type choose karke **Drive ya YouTube ka link** paste karo.
- Kisi bhi material pe click karoge to preview modal khulega (Drive files ke liye "Anyone with the link → Viewer" sharing ON honi chahiye, warna preview nahi chalega).
- 🕑 icon se manually likh sakte ho "kahan tak dekha" (jaise "10 min / 20 min") — ye Sheet me save hoga aur har device pe dikhega.
- Sab kuch Google Sheet me store hota hai — mobile se add karo ya laptop se, sab jagah same data dikhega.

## Dhyan rakhne wali baatein
- Drive files **"Anyone with the link"** share setting pe honi chahiye, warna preview modal me "naye tab me kholo" hi karna padega.
- Sheet directly edit mat karo jab tak zaroori na ho — column order (`Subject, Chapter, Material Type, Material Name, Link, Progress, Added On`) same rehna chahiye.
