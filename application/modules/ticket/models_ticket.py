__author__ = 'wilrona'

from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel

from ..user.models_user import UserModel
from ..agency.models_agency import AgencyModel
from ..currency.models_currency import CurrencyModel, EquivalenceModel
from ..customer.models_customer import CustomerModel
from ..departure.models_departure import DepartureModel, TravelModel
from ..ticket_type.models_ticket_type import ClassTypeModel, TicketTypeNameModel, JourneyTypeModel
from ..question.models_question import QuestionModel


class TicketPoly(polymodel.PolyModel):
    sellpriceAg = ndb.FloatProperty()
    sellpriceAgCurrency = ndb.KeyProperty(kind=CurrencyModel)

    type_name = ndb.KeyProperty(kind=TicketTypeNameModel)
    class_name = ndb.KeyProperty(kind=ClassTypeModel)
    journey_name = ndb.KeyProperty(kind=JourneyTypeModel)
    travel_ticket = ndb.KeyProperty(kind=TravelModel)

    agency = ndb.KeyProperty(kind=AgencyModel)
    is_prepayment = ndb.BooleanProperty(default=True)
    statusValid = ndb.BooleanProperty(default=True)
    is_return = ndb.BooleanProperty(default=False)

    selling = ndb.BooleanProperty(default=False)
    is_ticket = ndb.BooleanProperty(default=True)
    date_reservation = ndb.DateTimeProperty()
    sellprice = ndb.FloatProperty()
    sellpriceCurrency = ndb.KeyProperty(kind=CurrencyModel)

    customer = ndb.KeyProperty(kind=CustomerModel)
    departure = ndb.KeyProperty(kind=DepartureModel)

    ticket_seller = ndb.KeyProperty(kind=UserModel)
    e_ticket_seller = ndb.KeyProperty(kind=UserModel)
    is_boarding = ndb.BooleanProperty(default=False)
    generate_boarding = ndb.BooleanProperty(default=False)

    datecreate = ndb.DateTimeProperty()
    date_update = ndb.DateTimeProperty(auto_now=True)

    def make_to_dict_poly(self):
        to_dict = {}
        to_dict['ticket_allocated_id'] = self.key.id()
        if self.sellpriceAgCurrency:
            to_dict['sellpriceAgCurrency'] = self.sellpriceAgCurrency.id()
            to_dict['sellpriceAg'] = self.sellpriceAg

        to_dict['type_name'] = self.type_name.id()
        to_dict['class_name'] = self.class_name.id()

        to_dict['journey_name'] = None
        if self.journey_name:
            to_dict['journey_name'] = self.journey_name.id()

        to_dict['travel_ticket'] = None
        if self.travel_ticket:
            to_dict['travel_ticket'] = self.travel_ticket.id()

        to_dict['agency'] = None
        if self.agency:
            to_dict['agency'] = self.agency.id()

        to_dict['is_prepayment'] = self.is_prepayment
        to_dict['statusValid'] = self.statusValid
        to_dict['is_return'] = self.is_return

        to_dict['selling'] = self.selling
        to_dict['is_ticket'] = self.is_ticket
        to_dict['is_boarding'] = self.is_boarding

        if self.customer:
            to_dict['customer'] = self.customer.id()
        if self.departure:
            to_dict['departure'] = self.departure.id()

        to_dict['datecreate'] = str(self.datecreate)

        # pour un ticket vendu en ligne
        if self.ticket_seller:
            to_dict['ticket_seller'] = self.ticket_seller.id()

        to_dict['date_reservation'] = str(self.date_reservation)

        if self.sellpriceCurrency:
            to_dict['sellpriceCurrency'] = self.sellpriceCurrency.id()
            to_dict['sellprice'] = self.sellprice


        to_dict['child_return'] = []
        child = TicketModel.query(
            TicketModel.parent_return == self.key
        )
        for child in child:
            to_dict['child_return'].append(child.make_to_dict())

        return to_dict


class TicketModel(TicketPoly):
    upgrade_parent = ndb.KeyProperty(kind=TicketPoly)
    is_upgrade = ndb.BooleanProperty(default=False)
    is_count = ndb.BooleanProperty(default=True)
    parent_return = ndb.KeyProperty(kind=TicketPoly)
    parent_child = ndb.KeyProperty(kind=TicketPoly)

    def answer_question(self):
        answer = TicketQuestion.query(
            TicketQuestion.ticket_id == self.key
        )
        return answer

    def make_to_dict(self):
        to_dict = self.make_to_dict_poly()

        to_dict['parent_child'] = None
        if self.parent_child:
            to_dict['parent_child'] = self.parent_child.id()

        return to_dict


# class TicketParent(TicketPoly): #TICKET VIRTUEL GENERE PAR UN TICKET ALLE ET RETOUR. IL N'EST PAS COMPTABILISE
# parent = ndb.KeyProperty(kind=TicketModel)

class TicketQuestion(ndb.Model):
    question_id = ndb.KeyProperty(kind=QuestionModel)
    ticket_id = ndb.KeyProperty(kind=TicketModel)
    response = ndb.BooleanProperty(default=False)
