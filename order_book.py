from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def process_order(order):
    #Your code here
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
    print(current_order.id)
    print(current_order.timestamp)

    # Check if there are any existing orders that match.
    # orders = session.query(Order).filter(Order.filled == None).all()
    # for existing_order in orders:
    #     print(existing_order.id)
    #     print(existing_order.timestamp)



    # process_order(new_order)

    pass
