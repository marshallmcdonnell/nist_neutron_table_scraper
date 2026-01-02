import json
from typing import Union
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

class IsotopeData(BaseModel):
    isotope: str
    abundance: Union[float, None]
    coh_b: Union[float, None]
    incoh_b: Union[float, None]
    coh_xs: Union[float, None]
    incoh_xs: Union[float, None]
    scatt_xs: Union[float, None]
    abs_xs: Union[float, None]

class ElementData(BaseModel):
    element: str
    url: str
    isotopes: list[IsotopeData]

#======== Scraper =======

TIMEOUT=0.75
COLUMNS_PER_ROW = 8


# Base URL for the NIST page that lists elements
base_url = "https://www.ncnr.nist.gov/resources/n-lengths/elements/"

# Function to get the list of element links from the master page
def get_element_links():
    response = requests.get(base_url, timeout=TIMEOUT)

    if response.status_code != 200:
        print(f"Failed to retrieve the master page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    # Find all links to element pages
    # From inspecting the page, we know they are in <a> tags with 'href' attributes
    links = soup.find_all("a", href=True)

    # Filter out any links that don't correspond to element pages (e.g., excluding non-element links)
    element_links = [link['href'] for link in links if link['href'].endswith('.html')]

    return element_links

def clean_isotope_data(data_row) -> list[Union[str, float, None]]:

    # Have to use this for loop to modify list in place
    for i in range(len(data_row)):

        # Change concentrations of form (18.10 a) to just 18.10
        if 'a' in data_row[i]:
            data_row[i] = data_row[i].replace(' a','').replace('(','').replace(')','')

        # Change concentrations of form (7.37E3 to just 7.37E3
        if 'E' in data_row[i] and '(' in data_row[i]:
            data_row[i] = data_row[i].replace('(','').replace(')','')


        # Set to None if '---'
        data_row[i] = None if data_row[i] == '---' else data_row[i]

        if data_row[i] is None:
            continue

        # Remove leading '(+/-)' if present
        if data_row[i][0:5] == "(+/-)":
            data_row[i] = data_row[i][5:]

        # Change concentrations of the form (18.10) to just 18.10
        if data_row[i][0] == '(' and data_row[i][-1] == ')':
            data_row[i] = data_row[i][1:-1]

        # Remove leading < or > if present
        if data_row[i][0] in ['<', '>']:
            data_row[i] = data_row[i][1:]

        # Remove uncertainty in parentheses if present (i.e. 1.234(5) -> 1.234)
        if '(' in data_row[i]:
            data_row[i] = data_row[i].split('(')[0]

        # Drop complex component if present (i.e. 1.234-0.567i -> 1.234)
        if 'i' in data_row[i] and i != 0:
            complex_value = complex(data_row[i].replace('i','j'))
            data_row[i] = complex_value.real

        data_row[i] = float(data_row[i]) if i != 0 else data_row[i]  # First column is isotope name

    return data_row

# Function to scrape the "scatt xs" value for each element page
def scrape_scatt_xs(element_link) -> ElementData | None:
    url = base_url + element_link
    print(f"Scraping URL: {url}")
    response = requests.get(url, timeout=TIMEOUT)

    if response.status_code != 200:
        print(f"Failed to retrieve {element_link}. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    #scatt_xs = soup.find(string=lambda text: "scatt xs" in text.lower())
    #scatt_xs = soup.find(text="Scatt xs").find_next("td").text.strip()
    table = soup.find("table", attrs={"border": "4"})
    if table is None:
        return None

    rows = table.find_all("tr")


    # First data row after headers
    for row in rows:
        tds = row.find_all("td")
        if not tds:
            continue

        isotope_table = tds[0].text.strip()

        # Check for values that look like (7.37E3 a) and don't split over the space between number and 'a'
        if '(a)' in isotope_table or ' a' in isotope_table:
            isotope_table = isotope_table.replace('(a)','').replace(' a','')
        data = isotope_table.split()

        # Create element model to hold isotope data
        element_data = ElementData(
            element=element_link.replace('.html','').capitalize(),
            url = url,
            isotopes=[],
        )

        # Loop over each isotope (8 columns per isotope)
        for i in range(0, len(data), COLUMNS_PER_ROW):

            isotope_data = clean_isotope_data(data[i:i+COLUMNS_PER_ROW])

            isotope_data_model = IsotopeData(
                isotope = isotope_data[0],
                abundance = isotope_data[1],
                coh_b = isotope_data[2],
                incoh_b = isotope_data[3],
                coh_xs = isotope_data[4],
                incoh_xs = isotope_data[5],
                scatt_xs = isotope_data[6],
                abs_xs = isotope_data[7],
            )

            element_data.isotopes.append(isotope_data_model)

        break  # Only process the first data row



    return element_data


def format_row(key, values):
    nums = []
    for v in values:
        if v is None:
            nums.append(f"{'null':>10}")
        elif isinstance(v, float):
            nums.append(f"{v:10.6f}")
        else:
            nums.append(f"{str(v):>10}")

    return f"{key:5} : [ " + ", ".join(nums) + " ]"


print("Scraping scattering cross-section values from NIST...")
element_links = get_element_links()
print("Found elements:", element_links)

# Loop through all elements and print their "scatt xs" values

with open("out.yaml", "w") as f:

    f.write(
        "# "
        "abundance "
        "Coh_b (n) "
        "Incoh_b (n) "
        "Coh_xs (n) "
        "Incoh_xs (n) "
        "Scatt_xs (n) "
        "Abs_xs (n) "
        "\n"
    )

    for element in element_links:

        print(f"Processing element link: {element}")
        element_data= scrape_scatt_xs(element)
        if element_data:
            print(json.dumps(element_data.dict(), indent=2))

            for iso in element_data.isotopes:
                f.write(
                    format_row(
                        iso.isotope,
                        [
                            iso.abundance,
                            iso.coh_b,
                            iso.incoh_b,
                            iso.coh_xs,
                            iso.incoh_xs,
                            iso.scatt_xs,
                            iso.abs_xs,
                        ],
                    ) + "\n"
                )
