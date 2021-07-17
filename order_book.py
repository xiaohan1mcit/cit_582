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

    print(type(order))

    # Insert the order into the database
    order_obj = Order(sender_pk=order['sender_pk'],
                      receiver_pk=order['receiver_pk'],
                      buy_currency=order['buy_currency'],
                      sell_currency=order['sell_currency'],
                      buy_amount=order['buy_amount'],
                      sell_amount=order['sell_amount'])
    print(type(order_obj))
    session.add(order_obj)
    session.commit()

    # get the order you just inserted from the DB
    current_order = session.query(Order).order_by(Order.id.desc()).first()
    print(type(current_order))
    
    pass
