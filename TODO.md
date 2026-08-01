# Thesis
## MI-támogatott jogi ügyfél-előszűrő és ügyvéd-ajánló webalkalmazás tervezése, megvalósítása és értékelése.

Strukturáltan felveszi a felhasználó problémáját, egy korlátozott taxonómia szerint előzetes ügytípust javasol, majd magyarázható módon három megfelelő ügyvédprofilt ajánl. Alacsony bizonyosságnál kérdezzen vissza, vagy mondja ki, hogy nem tud felelősen besorolást adni.

1. lépés:
-megosztás bilickiv@gmail.com 
-README a problémával, célcsoporttal és termékhatárral; 
-egyoldalas MVP-leírás és priorizált backlog; 
-piackutatási összehasonlító táblázat; 
-jogterületi taxonómia és címkézési szabályok; 
-use case- és pageflow-vázlat; 
-első adatmodell és architektúraábra; 
-mérési és validációs terv; 
-adatvédelmi, jogi, MI- és biztonsági kockázati lista; 
-MI-használati napló. 

## Tervezett MVP-sorozat:
### MVP-0 – mérési és domainalap
válassz 6–8 pontosan definiált jogterületet vagy ügytípust;
készíts ügyvédprofil-sémát: szakterület, helyszín, nyelv, online vagy személyes konzultáció, elérhetőség, díjmodell;
állíts össze 100–200 címkézett, anonimizált vagy szakmailag ellenőrzött szintetikus ügyleírást;
készíts egyszerű szabályalapú besorolási és ajánlási baseline-t;
előre rögzítsd a mérőszámokat és a tesztadatokat.

A méréshez érdemes előre rögzíteni:
ügytípus-besorolás: macro-F1 és osztályonkénti recall;
információkinyerés: mezőszintű precision, recall és F1;
OCR: karakter- vagy szóhibaarány;
ajánlás: Precision@3, MRR vagy nDCG@3;
üzemeltetés: válaszidő, költség lekérdezésenként és hibaarány;
felhasználói oldal: feladatvégzési arány, idő és az ajánlások érthetősége.

### MVP-1 – működő termékmag
a felhasználó szövegesen leírja a problémáját;
a rendszer strukturált kérdésekkel bekéri a hiányzó adatokat;
ügytípust javasol bizalmi értékkel;
tartalomalapú pontozással három ügyvédprofilt ajánl (tartalomalaú, több szempontos rangsorolás legyen, amely figyelembe veszi az ügytípust, helyszínt, nyelvet, elérhetőséget és a konzultáció formáját. Erre később épülhet szemantikus hasonlóság vagy tanulható rangsorolás.);
az ajánlások mellett megmutatja azok indokait;
legyen egyszerű adminfelület a kategóriák és profilok kezelésére.

### MVP-2 – dokumentumfeldolgozás
először a PDF-ben már meglévő szöveget nyerd ki, OCR csak a szkennelt vagy képalapú iratoknál szükséges;
legyen személyesadat-felismerés és -maszkolás;
a rendszer strukturált mezőket nyerjen ki, és mutassa meg, melyik oldal vagy szövegrész alapján tette ezt;
alacsony megbízhatóságú adatnál kérjen felhasználói megerősítést;
valós jogi iratok helyett először anonimizált vagy szintetikus tesztanyaggal dolgozz.

### MVP-3 – összehasonlítás és validáció
hasonlíts össze egy szabályalapú baseline-t, egy embeddinges vagy szemantikus módszert és egy LLM-alapú besorolást;
ne csak pontosságot mérj, hanem válaszidőt, költséget, hibamintákat és azt is, milyen gyakran kell a rendszernek tartózkodnia a választól;
az ajánlásnál mérj top-3 relevanciát, szakértői vagy előre címkézett referencia alapján;
végezz kisebb felhasználói tesztet arra, hogy érthető-e az előszűrés és az ajánlások indoklása.

Modularizált alkalmazás: 
Külön ügyfél-intake, dokumentumfeldolgozó, besoroló és ajánló, LLM-gateway, valamint audit- és mérési modul.
Külön szolgáltatás kiemelése, ha arra konkrét indok van, pl. eltérő skálázás, hosszú háttérfeldolgozás vagy erősebb adatbiztonsági izoláció.

Kiegészítő vizsgálati irány:
A fejlesztési folyamat MI-támogatása jó kiegészítő vizsgálati irány, de ne legyen a termék mellett egy második teljes kutatás.
Egy jól körülhatárolt modulnál összehasonlíthatod az autonóm agentic és a felügyelt MI-támogatott munkafolyamatot azonos követelmények mellett. 
Mérheted a fejlesztési időt, az emberi beavatkozások számát, a teszteredményeket, a hibákat és az utólagos javítási időt. Ehhez kezdettől vezess MI-használati naplót.

Kiemelten fontos a felelős működés. A feltöltött jogi iratok érzékeny személyes adatokat tartalmazhatnak, és az MI téves besorolása valós kárt okozhat.
A dolgozat egyik szakmai értéke éppen az lehet, hogy bemutatod a bizonytalanság kezelését, az emberi megerősítést, a forráshelyek visszamutatását, 
az adatminimalizálást és azt, hogy a rendszer nem helyettesíti az ügyvédi tanácsadást.
