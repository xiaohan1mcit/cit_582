from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def process_order(order):
    # Your code here
    # type of order is <class 'dict'>

    # Insert the order into the database
    # type of order_obj is <class 'models.Order'>
    order_obj = Order(sender_pk=order['sender_pk'],
                      receiver_pk=order['receiver_pk'],
                      buy_currency=order['buy_currency'],
                      sell_currency=order['sell_currency'],
                      buy_amount=order['buy_amount'],
                      sell_amount=order['sell_amount'])
    session.add(order_obj)
    session.commit()

    process_order_inner()

    pass


def process_order_inner():
    # get the order you just inserted from the DB
    current_order = session.query(Order).order_by(Order.id.desc()).first()

    # Check if there are any existing orders that match.
    order_list = []
    orders = session.query(Order).filter(Order.filled == None).all()
    for existing_order in orders:
        if ((existing_order.buy_amount != 0) and (current_order.sell_amount != 0)):
            if ((existing_order.buy_currency == current_order.sell_currency)
                    and (existing_order.sell_currency == current_order.buy_currency)
                    and (existing_order.sell_amount / existing_order.buy_amount
                         >= current_order.buy_amount / current_order.sell_amount)
                    and (existing_order.counterparty_id == None)):
                order_list.append(existing_order)

    # If a match is found between order and existing_order
    if (len(order_list) > 0):
        match_order = order_list[0]

        # Set the filled field to be the current timestamp on both orders
        # Set counterparty_id to be the id of the other order
        match_order.filled = datetime.now()
        current_order.filled = datetime.now()
        match_order.counterparty_id = current_order.id
        current_order.counterparty_id = match_order.id
        session.commit()

        # when both orders can completely fill each other
        # if ((current_order.buy_amount <= existing_order.sell_amount)
        #         and (current_order.sell_amount >= existing_order.buy_amount)):

        # If existing_order is not completely filled
        if ((current_order.buy_amount <= existing_order.sell_amount)
            and (current_order.sell_amount <= existing_order.buy_amount)):
            diff = existing_order.buy_amount - current_order.sell_amount
            exchange_rate_existing = existing_order.sell_amount / existing_order.buy_amount
            sell_amount_new_existing = diff * exchange_rate_existing
            new_order = Order(sender_pk=existing_order.sender_pk,
                              receiver_pk=existing_order.receiver_pk,
                              buy_currency=existing_order.buy_currency,
                              sell_currency=existing_order.sell_currency,
                              buy_amount=diff,
                              sell_amount=sell_amount_new_existing,
                              creator_id=existing_order.id)
            session.add(new_order)
            # existing_order.child = new_order
            session.commit()
            process_order_inner()

        # If current_order is not completely filled
        if ((current_order.buy_amount >= existing_order.sell_amount)
                and (current_order.sell_amount >= existing_order.buy_amount)):
            diff = current_order.buy_amount - existing_order.sell_amount
            exchange_rate_current = current_order.buy_amount / current_order.sell_amount
            sell_amount_new_current = diff / exchange_rate_current
            new_order = Order(sender_pk=current_order.sender_pk,
                              receiver_pk=current_order.receiver_pk,
                              buy_currency=current_order.buy_currency,
                              sell_currency=current_order.sell_currency,
                              buy_amount=diff,
                              sell_amount=sell_amount_new_current,
                              creator_id=current_order.id)
            session.add(new_order)
            # current_order.child = new_order
            session.commit()
            process_order_inner()
