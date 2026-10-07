"""Collection objects and their loans."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import is_overdue, loan_label, urgency

TableModel = pxt.model_base()


class Objects(TableModel, name='objects'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    accession: pxt.String
    title: pxt.String
    medium: pxt.String
    year: pxt.Int
    gallery: pxt.String

    accession_upper = pxtf.string.upper(accession)
    title_lower = pxtf.string.lower(title)


class Loans(TableModel, name='loans'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    accession: pxt.String
    borrower: pxt.String
    venue: pxt.String
    status: pxt.String
    days_out: pxt.Int
    notes: pxt.String | None
    curator: pxt.String

    label = loan_label(accession, borrower, venue)
    overdue = is_overdue(status, days_out)
    urgency_band = urgency(status, days_out)
