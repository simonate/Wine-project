from multiprocessing import Pool
from requests_html import HTMLSession
import pandas as pd

session = HTMLSession()

def get_product_info(url):
    print(f"Processing URL {url}")

    url = url.strip()
    session = HTMLSession()
    web = session.get(url)
    product_info = web.html.find(".product-info")
    #defaultne nastavenie hodnoty, pokial sa neprepise v dalsom cykle, bude False
    #ratam s moznostou, ze siricitany tam nebudu
    #urcenie kategorie produktu
    df_dict = {
        "Víno obsahuje siričitany": False,
        "Kategória produktu": "Červené víno"
      }
    nazov_produktu = web.html.find(".content h1", first=True)
    df_dict["nazov_produktu"] = nazov_produktu.text

    for info in product_info:
        product_id = web.html.find("input[name='product']", first=True)
        df_dict["product_id"] = int(product_id.attrs["value"])

        #list slicing podla prazdnych riadkov 
        split = info.text.split("\n")
        #vlastnosti na webe su definovane podla tohto vzoru - farba: biele vino, preto:
        for line in split:
            name_value = line.split(":")

            if len(name_value) == 2:
                name = name_value[0]
                value = name_value[1]
                df_dict[name] = value
            elif len(name_value) == 1:
                #predpokladame, ze ide o 'Víno obsahuje siričitany', preto prepisem hodnotu na True
                name = name_value[0]
                df_dict[name] = True
            else:
                #v pripade ineho poctu prvkov program skonci a necham si vypisat aka hodnota to bola
                print("Chyba, je tam viac nez 1 ':'")
                print(url)
                print(name_value)

                raise ValueError("Neocekavany pocet ':'")

    return pd.DataFrame(df_dict, index=[0])



def get_champagne():
    zoznam_url = []

    for increment in range(1, 28):
        url = f"https://www.wineshop.sk/cervene-vino?p={increment}"
        stranka = session.get(url)
        print(f"increment {increment}")
        odkazy_vin = stranka.html.find(".w-list-item-title")
        enumerate_odkazy_vin = list(enumerate(odkazy_vin[:24]))
        for i,j in enumerate_odkazy_vin:
          i += 1
          web = j.attrs["href"]
          zoznam_url.append(web)

    return zoznam_url

if __name__ == "__main__":
    champagnes = get_champagne()

    with Pool() as pool:
        dataframes = pool.map(get_product_info, champagnes)
    print(dataframes)

    vina = pd.concat(dataframes, ignore_index = True)
    #clean_vina = vina.drop_duplicates(keep = False)
    print(vina)
    #odstranim poslednych 12 zaznamov, kedze na posl stranke sa ich nachadza len 12
    #vina_final = vina.iloc[:180]
    vina.to_csv("cervene_vina.csv", encoding="utf-8")

