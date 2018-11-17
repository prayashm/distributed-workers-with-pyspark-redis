import responder
from models import *
from tabulate import tabulate

api = responder.API()


def valid_date(datestring: str) -> bool:
    try:
        datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False


@api.route('/')
def hello(req, resp):
    resp.text = (
        'endpoints:\n'
        '    /getRecentItem/{YYYY-MM-DD:date}\n'
        '    /getBrandsCount/{YYYY-MM-DD:date}\n'
        '    /getItemsbyColor/{str:color}'
    )


@api.route('/getRecentItem/{queryDate}')
async def getRecentItem(req, resp, *, queryDate):
    if not valid_date(queryDate):
        resp.text = "Incorrect date format, should be YYYY-MM-DD"
        resp.status_code = api.status_codes.HTTP_400
        return

    product = RecentProduct(queryDate).get()
    if product is not None:
        response = json.loads(product.decode('utf-8'))
        resp.text = (f"id: {response['id']}\n"
                     f"brand: {response['brand']}\n"
                     f"colors: {response['colors']}")
    else:
        resp.text = f"No Item for date: {queryDate}"


@api.route('/getBrandsCount/{queryDate}')
async def getBrandsCount(req, resp, *, queryDate):
    if not valid_date(queryDate):
        resp.text = "Incorrect date format, should be YYYY-MM-DD"
        resp.status_code = api.status_codes.HTTP_400
        return

    counts = BrandCount(queryDate).get()
    if len(counts) > 0:
        resp.text = tabulate(counts, headers=(
            'brand', 'count'), tablefmt='psql')
    else:
        resp.text = f"No Brand Count for date: {queryDate}"


@api.route('/getItemsbyColor/{color}')
async def getItemsbyColor(req, resp, *, color):
    products = RecentProductsByColor(color).get()
    if len(products) > 0:
        products = [json.loads(p.decode('utf-8')) for p in products]
        resp.media = products
    else:
        resp.text = f"No Items for date: {queryDate}"

if __name__ == '__main__':
    print('Initializing ...')
    r.set('REACHABLE', 1)
    import init
    api.run()
