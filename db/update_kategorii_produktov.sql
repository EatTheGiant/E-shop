/*
    1	"Zábava, náučné"
    2	"Pre ženy"
    4	"Pre mužov"
    3	"Detské"
    5	"Šport a voľný čas"
    6	"Domov, záhrada, varenie"
    7	"Spoločnosť, ekonomika"
    8	"Počítače"
    9	"Cestovanie, príroda"
*/

--select * from tab_produkty where pro_nazov like '%pre_zeny%';


update tab_produkty set kat_kod = 2, pro_nazov = 'Blesk pro ženy', pro_popis = 'Český ženský týždeník', pro_cena = 0.50 where pro_nazov like '%pre_zeny%';
update tab_produkty set kat_kod = 2, pro_nazov = 'Maminka', pro_popis = 'Časopis Maminka sa venuje otázkam tehotenstva, pôrodu, zdravia, vývoja a výchovy detí', pro_cena = 2.30 where pro_nazov like '%maminka%';

update tab_produkty set kat_kod = 3, pro_nazov = 'ABC', pro_popis = 'Časopis ABC je legendárny dvojtýždenník pre deti vo veku 9-14 rokov', pro_cena = 1.50 where pro_nazov like 'abc_%';
update tab_produkty set kat_kod = 3, pro_nazov = 'Šikulka', pro_popis = 'Časopis Šikulka je nový mesačník určený pre zvedavé deti vo veku 3–7 rokov', pro_cena = 0.90  where pro_nazov like 'sikulka%';

update tab_produkty set kat_kod = 4, pro_nazov = 'Hodinky & šperky', pro_popis = 'Časopis Hodinky & šperky je originálny český časopis s odborným zameraním na hodinky a šperky.', pro_cena = 3.20  where pro_nazov like 'hodinky%';

update tab_produkty set kat_kod = 4, pro_nazov = 'Stereo & Video', pro_popis = 'Stereo&Video - spotrebiteľský mesačník, ktorý prináša aktuálne informácie z oblasti spotrebnej elektroniky, audiovizuálnej, informačnej a telekomunikačnej techniky', pro_cena = 2.50 where pro_nazov like 'stereo%';


update tab_produkty set kat_kod = 5, pro_nazov = 'Hattrick', pro_popis = 'Hattrick je český futbalový magazín, ktorý informuje čitateľov o správách z domova, aj zo zahraničia', pro_cena = 2.70 where pro_nazov like 'hattr%';

update tab_produkty set kat_kod = 6, pro_nazov = 'Bydlení', pro_popis = 'Český časopis o kultúre bývania - nápady a inšpirácie', pro_cena = 2.10 where pro_nazov like 'bydl%';
update tab_produkty set kat_kod = 6, pro_nazov = 'Můj dům', pro_popis = 'Můj dům je populárny český časopis o dome, stavbe domu a zariadenia bytu', pro_cena = 2.50 where pro_nazov like 'mujdum%';
update tab_produkty set kat_kod = 6, pro_nazov = 'Zahrádkář', pro_popis = 'Nejobľúbenejší český časopis o záhrade.', pro_cena = 2.50 where pro_nazov like 'zahrad%';
update tab_produkty set kat_kod = 6, pro_nazov = 'Receptář', pro_popis = 'Časopis Receptář je plný tipov a nápadov. Tento masačník je najstarší a najpredávanější český hobby magazín s pevnou základňou a viac ako 55 000 predplatiteľov', pro_cena = 1.20 where pro_nazov like 'recept%';

update tab_produkty set kat_kod = 7, pro_nazov = 'Reflex', pro_popis = 'Časopis Reflex - prestižny spoločenský týždeník je ostrovom slobodnej českej žurnalistiky.', pro_cena = 1.50 where pro_nazov like 'reflex%';
update tab_produkty set kat_kod = 7, pro_nazov = 'Forbes', pro_popis = 'Česká verzia prestižného amerického ekonomického magazínu Forbes', pro_cena = 3.50 where pro_nazov like 'forbs%';

update tab_produkty set kat_kod = 8, pro_nazov = 'Computer', pro_popis = 'Časopis Computer prináša novinky zo sveta počítačov, mobilných technológií a digitálnej techniky, analytické články a recenzie produktov', pro_cena = 3.99 where pro_nazov like 'compu%';
update tab_produkty set kat_kod = 8, pro_nazov = 'Level', pro_popis = 'Level je legendárny magazín o hrách a diania okolo nich, ktorý udalosti nepreberá, ale vyhľadáva a pozerá sa na ne z nečekaného uhlu', pro_cena = 4.50 where pro_nazov like 'level%';
update tab_produkty set kat_kod = 8, pro_nazov = 'SCORE', pro_popis = 'SCORE je najstarší pravidelne vychádzajúci český masačník o počítačových hrách', pro_cena = 6.50 where pro_nazov like 'score%';

update tab_produkty set kat_kod = 9, pro_nazov = 'Lidé a Země', pro_popis = 'Za obzorom čaká svet. Tradičný časopis o cestovaní na českom trhu Lidé a Země prináša svojim čitateľom exkluzivne reportáže.', pro_cena = 2.79 where pro_nazov like 'lideazeme%';
update tab_produkty set kat_kod = 9, pro_nazov = 'National Geographic', pro_popis = 'Prestižný cestopisný a poznávací časopis National Geographic s dlhoročnou tradiciou', pro_cena = 4.95 where pro_nazov like 'natgeo%';
update tab_produkty set kat_kod = 9, pro_nazov = 'Koktejl', pro_popis = 'Český geografický magazín. Koktejl sprostredkuje jedinečné stretnutie s faunou, flórou, kultúrou a historiou', pro_cena = 3.60 where pro_nazov like 'koktejl%';

update tab_produkty set kat_kod = 8, pro_nazov = 'CAD', pro_popis = 'Časopis CAD je časopis pre manažerov a špecialistov v obore počítačom podporovaného návrhu. Venuje sa využívaniu CAx technológií.', pro_cena = 3.60 where pro_nazov = 'CAD';

update tab_produkty set pro_nazov = 'Epocha', pro_popis = 'Epocha patrí medzi nejobľúbenějšie a najčítanejšie české časopisy', pro_cena = 2.50 where pro_nazov like 'epoc%jpg%';
update tab_produkty set pro_nazov = 'FotoVideo', pro_popis = 'FotoVideo je populárny časopis o fotografovaní a tvorbe médií.', pro_cena = 3.70 where pro_nazov like 'FotoVideo%jpg%';
update tab_produkty set pro_nazov = 'Full Moon', pro_popis = 'Full Moon je magazín o hudbe a modernom životnom štýle.', pro_cena = 4.90 where pro_nazov like 'Fullmoon%jpg%';
update tab_produkty set pro_nazov = 'Rock&Pop', pro_popis = 'Tradičný český hudobný magazín Rock & Pop už takmer 25 rokov prináša fanúškom rockovej a populárnej hudby široký prehľad o dianí naprieč žánrov a generácií', pro_cena = 3.70 where pro_nazov like 'rockandpop%jpg%';



----------------------------------------------------------
select count(*) from tab_produkty where pro_nazov like '%jpg%';
select * from tab_produkty where pro_nazov like '%jpg%';


select * from tab_produkty where pro_nazov like 'cad%jpg%';