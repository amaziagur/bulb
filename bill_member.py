import load_readings
import datetime
from utils import TariffComputer
from calendar import monthrange


def create_kwh_per_range_map(readings):
    result = dict()
    prev_reading= None

    if len(readings) == 1:
        prev_reading = build_reading(readings[0])
        readings.append(prev_reading)

    for read in readings:
        if prev_reading:
            result[(to_date(prev_reading), to_date(read))] = (read['cumulative'] - prev_reading['cumulative']) / (to_date(read) - to_date(prev_reading)).days
        prev_reading = read
    return result


def build_reading(reading):
    entry_date = to_date(reading)
    prev_date = entry_date - datetime.timedelta(days=monthrange(entry_date.year, entry_date.month)[1])
    return {'cumulative': 0, 'readingDate': prev_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), 'unit': 'kWh'}


def get_kwh_for_specific_day(date, price_per_range_map):
    for k,v in price_per_range_map.items():
        if k[0] < date <= k[1]:
            return v

    return 0


def get_amount_for_date(bill_date, kwh_per_range_map, account_id):
    bill_date = datetime.datetime.fromisoformat(bill_date)
    start_bill_period = datetime.timedelta(days=monthrange(bill_date.year,bill_date.month)[1])
    amount = 0
    kwh = 0
    for d in daterange(bill_date - start_bill_period, bill_date):
        kwh_per_day = get_kwh_for_specific_day(d, kwh_per_range_map)
        amount += TariffComputer().metric(account_id).compute(kwh_per_day, 1)
        kwh += kwh_per_day

    return amount, kwh


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n+1)


def calculate_bill(member_id=None, account_id=None, bill_date=None):
    readings = load_readings.get_readings()
    amount = kwh = 0
    service = account_id
    entries = readings.get(member_id)[0].get('account-abc')
    for e in entries:
        if account_id == 'ALL':
            if e.get('gas', False):
                service = 'gas'
            else:
                service = 'electricity'

        if len(e.get(service)) > 0:
            entries =e.get(service)
            calc_amount, calc_kwh = calculate_for(service, bill_date, entries)
            amount += calc_amount
            kwh += calc_kwh

    return amount, kwh


def calculate_for(account_id, bill_date, entries):
    price_range_map = create_kwh_per_range_map(entries)
    amount, kwh = get_amount_for_date(bill_date, price_range_map, account_id)
    return amount, kwh


def to_date(this_month_reading_entry):
    return datetime.datetime.strptime(this_month_reading_entry['readingDate'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=None)


def calculate_and_print_bill(member_id, account, bill_date):
    """Calculate the bill and then print it to screen.
    Account is an optional argument - I could bill for one account or many.
    There's no need to refactor this function."""
    member_id = member_id or 'member-123'
    bill_date = bill_date or '2017-08-31'
    account = account or 'ALL'
    amount, kwh = calculate_bill(member_id, account, bill_date)
    print('Hello {member}!'.format(member=member_id))
    print('Your bill for {account} on {date} is £{amount}'.format(
        account=account,
        date=bill_date,
        amount=amount))
    print('based on {kwh}kWh of usage in the last month'.format(kwh=kwh))
