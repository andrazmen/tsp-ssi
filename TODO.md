## TODO
- (lokalno) briši env za von-network in tails-server, ker se jih zaganja v dockerju
- razmisli, če bi se cloudcontroller tudi instaliralo kar iz pip package-a (so potrebne modifikacije kode?)
- controller ne more hkrati zaganjati aca-py in cloudcontrollerja, če sta v različnih .venv (<s>se jih da v isti env?</s> Problem ker je treba downgradad aiohttp na 3.9.4 ker errorji..)
- aca-py je trenutno verzije 1.1.1, potrebno nadgradit

- <s>DIDEx trenutno narejen avtomatsko - ko nekdo sprejme naš javni invitation, se izvede DID exchange in vzpotavi povezava: treba narest ročni DID exchange</s> Oboje je možno
- preveri kateri parametri pri cred def in rev bi bili avtomatizirani
- <s>stestiraj vse revocation funkcije</s>
- <s>stestiraj /revoke (kaj potrebuješ za revoke - cred_ex_id, ali cred-rev_id in rev_reg_id)</s>
- preveri, če je potreben v praksi še kakšen endpoint iz revocation APIjev

- issue VC: preveri parametre sporočil offer, request, proposal... predvsem attributes in replacement_id (v smislu, da nov VC zamenja starega). Nastavljeno, da je flow automatic, če issuer začne z offer in ga holder sprejme.. v primeru, da se začne s proposal iz holderjeve strani, potem moramo ročno? (issue_atomated avtomatizira celoten flow, uporabno?)

- <s>get records, connections... omogoča filtriranje, zaenkrat requestas vse</s>

- revocation: get_rev_reg_issued_details() ne dela. Mislim, da je bug v cloudcontroller kodi

- issue-vc: <s>pošiljanje offerja glede na proposal ne deluje..</s> <s>Težave s proposal - odstranjanje, ker načeloma nima smisla. Holder lahko prosi za offer prek basic message protokola!</s> Ja ampak, potem se holder ne more pritoževati na offer s proposal!

- <s>stestiraj present vp: pri tem je nujen proposal, ker drugače verifier sploh ne ve kaj lahko zahteva! Problem pri vp request, ker mora requester (verifier) že v requestu zahtevat točno določene parametre, kar ni problem, če je verifier tudi izdajatelj scheme in ve katere atribute zajema. Verifier, ki ne more pridit so scheme, neve za katere atribute naj prosi. Treba jih bo hardcodad. ALSO: razmisli še glede non_revoked parametra - nas zanima interval kdaj ali samo gledamo, da je trenutno veljavna?</s>

- <s>ko vzpostavim povezavo, agent z invitationom ne doseže drugega agenta - dodal sem trust ping in je v enem izmed primerov delovalo, stestiraj večkrat!! Zdaj sem v invitation dodal auto-accept in deluje basic message! Enkrat dela, drugič ne, zdaj sem odstranil multi_use pri invitation in dela!</s>

- <s>stestiraj še revocation skupaj z vp!</s>

- <s>ostal sem pri present-proof: send_pres_request_free ima names passan kot parameter - stestiraj! enako naredi še za non_revoked da vzame trenutni timestamp in enako za ostale funkcije!</s>

**02/04:**
- <s>dodaj v matching vc, da vzame vc z najvišjim cred_rev_id</s>
- razišči kje je težava s preverjanjem vp-ja, ko ponovno izdamo vc (trenutno se vp zapiše v cache tudi če ni veljaven) - reši težavo ali pa dodaj, da se vp izven agenta preveri na ledgerjuu preden se shrani v cache

**03/04:**
- <s>preimenuj cache.py ker ne gre dejansko za cache + uredi fajle</s>

**04/04:**
- <s>opiši upravljanje universal in vcs kontrolerja</s> <s>spravi v lepšo, bolj kompaktno obliko</s>

**07/04:**
- lokalnega DID-a se ne da dejansko naredit.. se pa samodejno ustvari, če vzpostavljamo povezavo in pri tem ne določimo, da želimo uporabit javni did - POPRAVI USE CASE

Načrt:
- UC -> requirements -> funkcionalnosti iz seq diagramov -> kako se jih poimplementira
- podatkovni modeli
- vmesniki