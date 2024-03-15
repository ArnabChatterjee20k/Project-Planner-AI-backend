import os
def create_queue():
    queue = "celery.sqlite"
    if not os.path.exists(queue):
        with open(queue, 'w') as file:
            print("file created")
    