from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Template
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Define the HTML template with Materialize CSS for dark mode
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Product Details</title>
    <!-- Import Materialize CSS -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #121212;
            color: #ffffff;  
            font-size: 8px;
        }
        .card {
            background-color: #1e1e1e;
        }
        .card-image {
            width: 200px;
            margin: auto;
        }
        .card-image img {
            width: 100%;
            height: auto;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            color: #ffffff;
        }
        th {
            background-color: #333333;
        }
        .image-column {
            width: 200px;
        }
        .table-column {
            flex: 1;
        }
        .row {
            display: flex;
            flex-wrap: wrap;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="row">
            <div class="col s12 m4 image-column">
                <div class="card">
                    <div class="card-image">
                        <img src="{{ image_url }}" alt="Product Image">
                    </div>
                </div>
            </div>
            <div class="col s12 m8 table-column">
                <div class="card">
                    <div class="card-content">
                        <table>
                            <thead>
                                <tr>
                                    <th>Property</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for key, value in product_details.items() %}
                                <tr>
                                    <td>{{ key }}</td>
                                    <td>{{ value }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Import Materialize JavaScript -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
</body>
</html>
"""

@app.get("/product/{barcode}", response_class=HTMLResponse)
async def get_product_details(barcode: str):
    # URL of the product detail page
    url = f"https://upcitemdb.com/upc/{barcode}"
    # https://world.openfoodfacts.org/product/0643126971962

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table containing the product details
    table = soup.find('table', class_='detail-list')

    # Extract the rows from the table
    rows = table.find_all('tr')

    # Initialize a dictionary to store the product properties
    product_details = {}

    # Iterate over the rows and extract the property names and values
    for row in rows:
        cells = row.find_all('td')
        property_name = cells[0].text.strip().replace(":", "")
        property_value = cells[1].text.strip()
        product_details[property_name] = property_value

    # Find the image tag
    image_tag = soup.find('img', class_='product')

    # Extract the image URL
    image_url = image_tag['src']

    # Render the HTML template with the product details and image URL
    template = Template(html_template)
    html_content = template.render(product_details=product_details, image_url=image_url)

    return HTMLResponse(content=html_content)

# To run the app, use the command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
