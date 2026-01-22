import pandas as pd
from src.config import DATA_DIR

pl = pd.read_excel(f"{DATA_DIR}/wine-price-ru.xlsx")

country_map = {
    "IT": "Италия", "FR": "Франция", "ES": "Испания", "RU": "Россия", "PT": "Португалия",
    "AR": "Армения", "CL": "Чили", "AU": "Австралия", "GE": "Грузия", "ZA": "ЮАР",
    "US": "США", "NZ": "Новая Зеландия", "DE": "Германия", "AT": "Австрия", "IL": "Израиль",
    "BG": "Болгария", "GR": "Греция"
}

revmap = {v.lower(): k for k, v in country_map.items()}

def find_wines(req):
    x = pl.copy()
    if req.country and req.country.lower() in revmap:
        x = x[x["Country"] == revmap[req.country.lower()]]
    if req.acidity:
        x = x[x["Acidity"] == req.acidity.capitalize()]
    if req.color:
        x = x[x["Color"] == req.color.capitalize()]
    if req.name:
        x = x[x["Name"].str.contains(req.name, case=False, na=False)]
    if req.sort_order and len(x) > 0:
        if req.sort_order == "cheapest":
            x = x.sort_values(by="Price")
        elif req.sort_order == "most expensive":
            x = x.sort_values(by="Price", ascending=False)
    if x.empty:
        return "Подходящих вин не найдено"
    return "Вот какие вина были найдены:\n" + "\n".join(
        f"{z['Name']} ({country_map.get(z['Country'], 'Неизвестно')}) - {z['Price']}"
        for _, z in x.head(10).iterrows()
    )