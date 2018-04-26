from main import app, celery, db
import os, csv, random, time
from pim.models import *

@celery.task(bind=True)
def read_csv_file(self, path):
    """Background task to insert data in db."""
    total = random.randint(1, 100)
    for i in range(total):
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                })
        time.sleep(1)
    csv_data = path
    with open(csv_data) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # skip first line
        next(reader, None)
        for reader in reader:
            try:
                print ("inserting record in database")
                product_data = Product(name=reader[0],sku=reader[1],description=reader[2],is_active=True)
                db.session.add(product_data)
                db.session.commit()
                print ("Inserted record in database", product_data)
            except:
                print ("skipping record because of error================")
    # remove file from folder
    os.remove(path)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}