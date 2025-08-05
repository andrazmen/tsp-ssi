## TODO
- (lokalno) briši env za von-network in tails-server, ker se jih zaganja v dockerju
- razmisli, če bi se cloudcontroller tudi instaliralo kar iz pip package-a (so potrebne modifikacije kode?)
- controller ne more hkrati zaganjati aca-py in cloudcontrollerja, če sta v različnih .venv (<s>se jih da v isti env?</s> Problem ker je treba downgradad aiohttp na 3.9.4 ker errorji..)
- aca-py je trenutno verzije 1.1.1, potrebno nadgradit
- revocation: get_rev_reg_issued_details() ne dela. Mislim, da je bug v cloudcontroller kodi

### Načrt:
- UC -> requirements -> funkcionalnosti iz seq diagramov -> kako se jih poimplementira
- podatkovni modeli
- vmesniki