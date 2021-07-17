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
    # print(order['sell_currency'])
    # print(order['sell_amount'])

    # Insert the order into the database
    order_obj = Order(sender_pk=order['sender_pk'],
                      receiver_pk=order['receiver_pk'],
                      buy_currency=order['buy_currency'],
                      sell_currency=order['sell_currency'],
                      buy_amount=order['buy_amount'],
                      sell_amount=order['sell_amount'])
    session.add(order_obj)
    session.commit()

    # get the order you just inserted from the DB
    current_order = session.query(Order).order_by(Order.id.desc()).first()

    # Check if there are any existing orders that match.
    order_list = []
    orders = session.query(Order).filter(Order.filled == None).all()
    for existing_order in orders:
        if ((existing_order.buy_currency == current_order.sell_currency)
                and (existing_order.sell_currency == current_order.buy_currency)
                and (
                        existing_order.sell_amount / existing_order.buy_amount >= current_order.buy_amount / current_order.sell_amount)
                and (existing_order.counterparty_id == None)):
            order_list.append(existing_order)

    # If a match is found between order and existing_order
    if (len(order_list) > 0):
        print(len(order_list))

    # process_order(new_order)

    pass
