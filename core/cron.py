from core.models import * 

def DeleteUnassigned():
    deleted_count = UploadData.objects.filter(is_assigned=False).delete()
def my_scheduled_job():
    print("This is a scheduled job!")