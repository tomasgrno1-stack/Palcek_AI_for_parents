
# 📘 Palčekovia AI pre dospelých a rodičov

Odborná, vecná a prehľadná AI poradňa a asistent pre rodičov detí s achondropláziou a dospelých členov komunity **Palčekovia**.

## 🌟 Hlavné funkcie
* **Legislatíva a kompenzácie:** Informácie k žiadostiam o preukaz ŤZP, opatrovateľské príspevky a pomôcky (ÚPSVaR).
* **Zdravotná starostlivosť:** Prehľad odporúčaných špecialistov a preventívnych prehliadok.
* **Inkluzívne vzdelávanie:** Tipy na prípravu školských zariadení a prispôsobenie prostredia pre dieťa.
* **Spracovanie dokumentov:** Analýza a zhrnutie priložených lekárskych správ, PDF súborov a žiadostí.
* **Elegatný tmavý dizajn:** Prehľadné prostredie navrhnuté pre pohodlné čítanie rozsiahlejších textov.

## 🛠️ Použité technológie
* [Python 3.10+](https://www.python.org/)
* [Streamlit](https://streamlit.io/) – webové rozhranie
* [Google Gemini API](https://ai.google.dev/) (`gemini-2.0-flash`)
* [pypdf](https://pypdf.readthedocs.io/) & [python-docx](https://python-docx.readthedocs.io/) – spracovanie dokumentov

## 🚀 Nasadenie
Aplikácia je nasadená cez Streamlit Community Cloud. Pre lokálne spustenie:
```bash
pip install -r requirements.txt
streamlit run Palček_AI_pre_rodičov.py
