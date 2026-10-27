"""Outside-freeze settlement correction; same admission and phase ceilings."""
from decimal import Decimal
from muse_guard.gateway import Gateway, DollarBudget

class PhaseSettlement(DollarBudget):
    def __init__(self, limit, owner=None):
        super().__init__(limit)
        self.owner = owner

    def settle(self, usage):
        if usage is None:
            self.unknown = True
            return
        if self.unknown or self.pending <= 0:
            raise ValueError("Prior provider usage is unresolved")
        a, b, cached = (usage[k] for k in ('input_tokens','output_tokens','cached_input_tokens'))
        if any(type(x) is not int or x < 0 for x in (a,b,cached)) or cached > a:
            self.unknown = True
            raise ValueError("Invalid provider usage")
        actual = (Decimal(a-cached)*Decimal('1.25') + Decimal(cached)*Decimal('.15') + Decimal(b)*Decimal('4.25'))/1000000
        reserved = self.pending
        # The phase allowance is already reserved in the shared daily ledger.
        # Known provider usage is not an unknown receipt simply because the
        # provider exceeded a smaller per-request estimate.
        self.spent += actual
        self.pending = Decimal(0)
        if self.owner is not None:
            event = self.owner.events[-1]
            event['settlement'] = {'actual_usd':float(actual),'request_reserved_usd':float(reserved),
                                   'phase_spent_usd':float(self.spent),'phase_limit_usd':float(self.limit),
                                   'exceeded_request_estimate':actual > reserved}
            measured = sum(e['usage']['input_tokens']+e['usage']['output_tokens']
                           for e in self.owner.events if e.get('usage') is not None)
            self.owner.budget.reserved_tokens = max(self.owner.budget.reserved_tokens, measured)
            if measured > self.owner.budget.limit:
                self.unknown = True
                raise ValueError("Provider exceeded phase token budget; stop")
        if self.spent > self.limit:
            self.unknown = True
            raise ValueError("Provider exceeded phase dollar quota; stop")

class ReconciledGateway(Gateway):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.dollars is not None:
            self.dollars = PhaseSettlement(self.dollars.limit, self)
