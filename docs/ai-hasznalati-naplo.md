### 2026.09.30 — [A tervezett projekt feature-einek összegyűjtése]

- **Eszköz:** Gemini Pro
- **Kategória:** `szövegezés`
- **Fájl:** 2026.09.30/Gemini.pdf
- **Mit kezdtem vele:** A kapott outputot alaposan átnéztem és átadtam Claude-nak User Story-k írásához
- **Átvett tartalom:** Teljes

### 2026.09.30 — [User Story-k megírása]

- **Eszköz:** Claude Opus 5.5 High
- **Kategória:** `ötletelés` / `szövegezés`
- **Fáj:** 2026.09.30/Claude
- **Mit kezdtem vele:** A kapott outputot alaposan átnéztem és nagyon alaposan átdolgoztam. A módosított verzió a User Stories mappában érhető el.
- **Átvett tartalom:** A fájl jelentősen át lett dolgozva. User story-kat adtam hozzá és vettem el, módosítottam rajtuk és a prioritásukon. A fájl egy útmutató volt, hogy pontosan hogyan is kéne kinéznie egy ilyen dokumentumnak a gyakorlatban.

### 2026.10.10 — [User stories - A referenciák javítása]

- **Eszköz:** Claude Opus 5.5 High
- **Kategória:** `szövegezés` 
- **Fájl:** 2026.10.10/Claude/US - Broken cross-references
- **Mit kezdtem vele:** A kapott outputot alaposan átellenőriztem és töröltem belőle adatokat, amiket nem implementálok az első iterációban, majd Claude-dal legeneráltam egy megfelelő promptot, amit Lovable-nek beadva legeneráltam a frontendet.
- **Átvett tartalom:** Mappában megtalálható a teljes output és a módosítás eredménye is.

### 2026.10.10 — [Frontend prompt generálása Lovable-nek]

- **Eszköz:** Claude Opus 5.5 High
- **Kategória:** `szövegezés`
- **Fájl:** 2026.10.10/Claude/Frontend prompt for Lovable
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### 2026.10.10 — [Frontend generálása]

- **Eszköz:** Lovable build
- **Kategória:** `kód`
- **Fájl:** 2026.10.10/Lovable
- **Mit kezdtem vele:** A kódot átnézem. Szükség esetén módosítok, törlök vagy kiegészítem. Amikor kész, elkezdem a backend-et építeni hozzá.
- **Átvett tartalom:**

### 2026.10.11 — [Kezdeti taxonómia és besorolási szabályok generálása]

- **Eszköz:** Calude Opus 5.5 Max
- **Kategória:**`ötletelés`
- **Fájl:** 2026.10.11/Claude/Taxonómia és besorolási szabályok.md
- **Mit kezdtem vele:** Kezdetben átveszem a teljes taxonómiát és besorolási szabályokat. Menet közben tapasztalat útján finomítok rajta és lehetőség szerint egy jogi szakemberrel átnézetem.
- **Átvett tartalom:** Teljes

### 2026.10.14 — [Új ügy felvételéhez szükséges kód generálása - HTML, view, form, url]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `kód`
- **Fájl:** 2026.10.14/Claude
- **Mit kezdtem vele:** A kódot alaposan átnéztem, majd javítottam rajta, mert hibás volt a prompt-om és kihagytam belőle részeket. A kapott információt, hogy {{form}} azonos a {{form.as_div}}-vel, a hivatalos dokumentációban leellenőriztem.
- **Átvett tartalom:** A kód legnagyobb részét felhasználtam, kivéve: html-ben a scriptet nem használtam fel, forms.py-ból a felesleges függvényeket kihagytam, views.py-ból a felesleges attribute beállításokat kihagytam.

### 2026.10.15 — [User és lawyer admin page formázása]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `kód`
- **Fájl:** 2026.10.15/Claude/User és lawyer admin page formázása.txt
- **Mit kezdtem vele:** A kódot átnéztem, megfelelőnek tartottam. Kiegészítettem az is_lawyer funkcióval a UserAdmin osztályt. A Language modellből kiszedtem a blank=True és null=True beállításokat, mert valóban nem szükségesek.
- **Átvett tartalom:** Teljes

### 2026.10.15 — [Az ajánlások oldal generálása]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `kód` 
- **Fájl:** 2026.10.15/Claude/Ajánlások oldal html-jének generálása
- **Mit kezdtem vele:** A változók neveit a megfelelőkre módosítottam, css kódot töröltem.
- **Átvett tartalom:** Html teljes egészében, kisebb módosításokkal

### 2026.10.22 — [Szöveg kinyerése pdf-ből txt-be]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `kód`
- **Fájl:** 2026.10.22 / PDF extraction
- **Mit kezdtem vele:** A kódot átnéztem, majd az összegyűjtött anonimizált kódleírásokon használtam
- **Átvett tartalom:** Teljes

### 2026.10.22 — [Txt-ben található szöveg lemmatizálása, lemmák és 2 hosszú lemma párok megszámolása, adatok visszaadása csv fájlban]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `ötletelés` / `kód` 
- **Fájl:** 2026.10.22 / Text lemmatization
- **Mit kezdtem vele:** A kód célja az ügyek leírásában szereplő szavak frekvenciájának meghatározása volt és egy szabályalapú osztályozási rendszer kialakítása. A kód jól működött, kísérleteztem is vele, de végül más megközelítés választottam. A lemmatizálás HuSpaCy-val történt.
- **Átvett tartalom:** A teljes kódot használtam, de a végleges megoldásban nem lesz benne.

### 2026.10.22 — [2 CSV fájl adataiból dictionary létrehozása]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `kód` 
- **Fájl:** 2026.10.22 / Creating dictionary based on csv files
- **Mit kezdtem vele:** Szófrekvenciák beolvasása dictionary-be. Szabályalapú osztályozás során kapott pont a szófrekvencia alapján van meghatározva. 1 CSV fájl 1 ügyi kategóriának felel meg, így szószám normalizására 100000 tokenszámra.
- **Átvett tartalom:** A prototípus készítése során a teljes kódot használtam. Ahogy egyre több kategóriával dolgozok, módosítanom kell a megoldást. A normalizálás célszerűbb lenne a szófrekvenciákat tartalmazó csv fájlok létrehozása közben.

### 2026.10.22 — [Szabályalapú osztályozás - egyedül álló lemmák és 2 vagy 3 szomszédos lemmapárok előfordulása]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `kód` 
- **Fájl:** 2026.10.22 / Creating legal keywords
- **Mit kezdtem vele:** 1. lépésben a szkript két jogi ügyleírásokat tartalmazó mappát vizsgál: a vizsgált jogterületét és egy referenciát. Az egyedülálló lemmákat és a 2 vagy 3 hosszú szomszédos lemmákat vizsgálja.
A vizsgált jogterületben előforduló szavak előfordulását elemzi a referencia mappában 
(a log_ratio azt fejezi ki, hogy a két kategóriában milyen arányban található meg egy bizonyos szó. Ha mind a kettőben gyakori, 
akkor a szó nem specifikus a vizsgált jogterületre, így a besoroláskor nem jár pont érte).
A megadott kritériumok alapján kiszűri a vizsgált jogterületre nem specifikus szavakat. A 2. lépésben az osztályozáskor használandó szavakat exportálja csv fájlba az előfordulásuk számával.
Lemmatizáláshoz HuSpaCy-t használtam.
A kód az első verzióban hiánytalanul használva van. A továbbiakban módosítok rajta (pl. az outputban az előfordulások normalizálása egy megadott szószámra).
- **Átvett tartalom:** Teljes, a továbbiakban módosításra kerül

### 2026.10.22 — [Kulcsszavak keresése a pontosító kérdésekhez]

- **Eszköz:** Calude Opus 5.5 High
- **Kategória:** `ötletelés` / `kód` 
- **Fájl:** 2026.10.22 / Find ambiguous keywords
- **Mit kezdtem vele:** A szkript 2 ügytípushoz tartalmazó 2-2 szófrekvenciákat tartalmazó csv fájlt vizsgál (az előző bejegyzés kódja által generált output).
Cél: azon szavak megtalálása, melyek gyakran előfordulnak önmagukban és más szóval párban, több különböző ügykategóriában úgy, hogy jelentős különbség az előfordulásuk számában.
Ha az ügyfél leírásában megtalálható egy ilyen kifejezés a rövidebb formájában, akkor értékes információt kaphatunk egy pontosító visszakérdezés alkalmazásával.
Eredmény: egy csv fájl, melyben ezek a szavak vannak felsorolva a pontszámukkal a különböző rövidebb és hosszabb formájukban.
A lista nagyon hosszú lett és nagyon kevés volt a gyakorlatban használható információ. A megoldáson pontosítani kell vagy más megközelítést választani.
- **Átvett tartalom:** A kódot kísérletezésre használtam. Az első verzióban egy kézzel készített táblázattal helyettesítettem. 
A jövőben vagy átdolgozom a megközelítést vagy más megoldást választok (más adatvezérelt vagy kézzel előállított).

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**

### ÉÉÉÉ.HH.NN — [rövid cím]

- **Eszköz:**
- **Kategória:** `megértés` / `ötletelés` / `kód` / `szövegezés` /
  `fordítás` / `irodalomkutatás`
- **Fájl:**
- **Mit kezdtem vele:**
- **Átvett tartalom:**