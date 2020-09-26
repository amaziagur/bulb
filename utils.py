from tariff import BULB_TARIFF


class TariffComputer(object):

    # @staticmethod
    def metric(self, type):
        self.type = type
        return self

    def __factory(self):
        if self.type == 'electricity':
            return ElectricityComputer()
        elif self.type == 'gas':
            return GasComputer()
            return None

    def compute(self, cumulative, total_billed_days):
        computer = self.__factory()
        total = computer._bill_cumulative_in_pence(cumulative) + computer._bill_fixed_daily_for_range_of(total_billed_days)
        # convert to GBP
        return total / 100


class ElectricityComputer(TariffComputer):

    @staticmethod
    def _bill_cumulative_in_pence(cumulative):
        return cumulative * BULB_TARIFF.get('electricity').get('unit_rate')

    @staticmethod
    def _bill_fixed_daily_for_range_of(days):
        return days * BULB_TARIFF.get('electricity').get('standing_charge')


class GasComputer(TariffComputer):

    @staticmethod
    def _bill_cumulative_in_pence(cumulative):
        return cumulative * BULB_TARIFF.get('gas').get('unit_rate')

    @staticmethod
    def _bill_fixed_daily_for_range_of(days):
        return days * BULB_TARIFF.get('gas').get('unit_rate')