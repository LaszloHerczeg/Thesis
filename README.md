# MI-támogatott jogi ügyfél-előszűrő és ügyvéd-ajánló webalkalmazás tervezése, megvalósítása és értékelése

## Leírás

### Probléma
Egy jogban nem jártas személy számára problémát okozhat a megfelelő ügyvéd megtalálása.  
Manapság szinte bármilyen szolgáltatást kényelmesen gyorsan meg lehet találni az interneten, amíg ügyvédek leginkább ajánlások útján találnak új ügyfeleket.  

### Cél
Egy olyan szolgáltatás létrehozása, amely segít az ügyfeleknek megtalálni a számukra leginkább megfelelő ügyvédet.  
Az ügyvédek támogatása az ügyfélkörük bővítésében.
MI-támogatott, könnyen kezelhető szolgáltatás formájában.

### Célcsoport
Ügyvédek, akik új ügyfeleket keresnek és nyitottak ezt online formában tenni.  
Ügyfelek, akiknek jogi segítségre van szüksége és szeretnék megtalálni a legmegfelelőbb jogi szakembert.

### Termékhatár
- Strukturáltan felveszi a felhasználó problémáját
- Egy korlátozott taxonómia szterint előzetes ügytípust javasol
- Magyarázható módon három megfelelő ügyvédprofilt ajánl
- Alacsony bizonyosságnál kérdezzen vissza vagy mondja ki, hogy nem tud felelősen besorolást adni

## Indítás (demó)

A demó videó a `demo-v1` tag-en lévő verzióval készült.
Az alábbi lépésekkel ugyanaz a működés reprodukálható.

### 1. Klónozás és a demó verzió
```
git clone <REPO_URL>
cd <PROJEKT_MAPPA>
git checkout demo-v1
```

### 2. Virtuális környezet és függőségek
```
python -m venv venv
```
Aktiválás:
- Windows: `venv\Scripts\activate`
- macOS/Linux: `source venv/bin/activate`

```
pip install -r requirements.txt
```

### 3. Környezeti változók (.env)
Másolja le a mintafájlt `.env` néven:
- Windows: `copy .env.example .env`
- macOS/Linux: `cp .env.example .env`

Új secret key generálása:
```
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
A kiírt értéket másolja be a `.env` fájlba:
```
SECRET_KEY=<a_generált_kulcs>
DEBUG=True
```

### 4. Adatbázis és tesztadatok
```
python manage.py migrate
python manage.py loaddata fixtures/demo_data.json
```

Tesztfelhasználók:

| Felhasználónév | Jelszó | Szerep |
| --- | --- | --- |
| teszt_admin | Demo2026Admin! | admin |


Saját admin felhasználó is létrehozható:
```
python manage.py createsuperuser
```

### 5. Indítás
```
python manage.py runserver
```
Az alkalmazás elérhető: http://127.0.0.1:8000/
Admin felület: http://127.0.0.1:8000/admin/

### 6. Videóban bemutatott tesztesetek (docs/tesztesetek)
1. házasság felbontása/7.txt
2. Lakásbérleti szerződés/1.txt
3. munkaviszony megszüntetése/3.txt
4. munkaviszony megszüntetése/3.txt