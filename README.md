**Upload products through csv file and schdule a celery task to precess them in background**

# Celery Worker

    celery worker -A main.celery --loglevel=info


# Restore db 

    python manage.py resetdb
    
 # Seed initial data or example data 
 
    python manage.py seed
    
 # run project 
  
    python manage.py runserver
 

