"""Museum Loans API built with Pixeltable.

    pxt schema update app.py museum
    pxt service run app.py museum
"""
from pixeltable.serving import FastAPIRouter

from models import Loans, Objects, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import overdue_loans

loans_api = FastAPIRouter(name='loans_api')
loans_api.add_insert_route(Objects, path='/objects',
                           inputs=[Objects.accession, Objects.title, Objects.medium, Objects.year, Objects.gallery],
                           outputs=[Objects.id, Objects.accession_upper, Objects.title_lower])
loans_api.add_insert_route(Loans, path='/loans',
                           inputs=[Loans.accession, Loans.borrower, Loans.venue, Loans.status, Loans.days_out,
                                   Loans.notes, Loans.curator],
                           outputs=[Loans.id, Loans.label, Loans.overdue, Loans.urgency_band])
loans_api.add_update_route(Loans, path='/loans/update', inputs=[Loans.status, Loans.days_out],
                           outputs=[Loans.id, Loans.overdue, Loans.urgency_band])
loans_api.add_compute_route(Loans, path='/urgency', inputs=[Loans.status, Loans.days_out],
                            outputs=[Loans.overdue, Loans.urgency_band])
loans_api.add_query_route(path='/loans/overdue', query=overdue_loans, method='get')
