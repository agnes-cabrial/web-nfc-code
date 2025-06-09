import boto3
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from core.models import UploadData
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from django.core.files.storage import default_storage
from django.contrib import messages
import json
from django.http import JsonResponse
from django.utils.timezone import now
# AWS S3 Bucket Setup
AWS_BUCKET_NAME = "s3zaisha-test"
logger = logging.getLogger(__name__)

def WriteNfc(request):
    return render(request, "base/writeNfc.html")

def Index(request):
    imei = request.GET.get("imei", None)
    update_type = request.GET.get("type", None)
    if imei:
        request.session['imei'] = imei
        if update_type == "update":
            request.session['update_mode'] = True
            return render(request, "base/index2.html", {"imei": imei, "update_mode": True})
        if UploadData.objects.filter(imei=imei).exists():
            stored_data = UploadData.objects.get(imei=imei) 
            if not stored_data.password:
                request.session['output_displayed'] = True
                return render(request, "base/output.html", {"all_data": [stored_data]})
            if request.method == "POST":
                entered_password = request.POST.get("password", "")
                if stored_data.password == entered_password:
                    request.session['output_displayed'] = True
                    return render(request, "base/output.html", {"all_data": [stored_data]})
                else:
                    messages.error(request, "Invalid password! Please try again.")
                    return render(request, "base/password_popup.html", {"imei": imei})
            return render(request, "base/password_popup.html", {"imei": imei})
        return render(request, "base/index2.html", {"imei": imei})
    return render(request, "base/index2.html", {"imei": None, "show_popup": True})

def set_password_page(request):
    imei = request.GET.get("imei", "") 
    return render(request, "base/setpasswordnfc.html", {"imei": imei})

def save_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) 
            imei = data.get("imei") 
            password = data.get("password") 
            
            if not imei:
                return JsonResponse({"success": False, "message": "Invalid IMEI."})

            if not password or len(password) != 4:
                return JsonResponse({"success": False, "message": "Invalid password length."})
            try:
                user_entry = UploadData.objects.get(imei=imei)
                user_entry.password = password 
                user_entry.created_at = now()  
                user_entry.save()
            except UploadData.DoesNotExist:
                user_entry = UploadData.objects.create(imei=imei, password=password)

            return JsonResponse({"success": True, "message": "Password saved successfully."})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data."})
    
    return JsonResponse({"success": False, "message": "Invalid request method."})

def OutputData(request, slug):
    upload = get_object_or_404(UploadData, slug=slug)
    imei = upload.imei
    all_data = UploadData.objects.filter(imei=imei)
    return render(request, "base/output.html", {"all_data": all_data, "imei": imei})

def SaveData(request):
    if request.method == "POST":
        image = request.FILES.get('image_file', None)
        video = request.FILES.get('video_file', None)
        audio = request.FILES.get('audio_file', None)
        is_password = request.POST.get('is_password', 'false').lower() == 'true'
        is_name = request.POST.get('name', "").strip()
        is_comments = request.POST.get('comments', "").strip()
        imei = request.session.get("imei", None)
        update_mode = request.session.get('update_mode', False)

        if imei:
            UploadData.objects.filter(imei=imei).delete()
        # if imei:
        #     existing_data = UploadData.objects.filter(imei=imei).first()
        #     if existing_data:
        #         logger.info("Existing data found: %s", existing_data)
        #         if existing_data.video or existing_data.photo or existing_data.recording:
        #             logger.info("Existing record has media. Deleting record...")
        #             existing_data.delete()
        upload = UploadData.objects.create(
            imei=imei,
            video=video,
            photo=image,
            recording=audio,
            is_name=is_name if is_name else None,
            is_comments=is_comments if is_comments else None,
            password_protected=is_password,
            password=request.POST.get('password') if is_password else None
        )
        request.session['is_name'] = is_name
        request.session['is_comments'] = is_comments

        logger.info("File saved successfully: %s", upload.slug)
        messages.success(request, "Successful saved")
        return redirect("core:output-data", slug=upload.slug)

    return render(request, "base/audio.html")

def AssignTag(request, slug):
    upload = get_object_or_404(UploadData, slug=slug)
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    imei = request.session.get("imei", None)
    is_name = request.session.pop('is_name', None)
    is_comments = request.session.pop('is_comments', None)

    all_data = UploadData.objects.filter(imei=imei) if imei else []

    try:
        for field in ["photo", "video", "recording"]:
            file_obj = getattr(upload, field)
            if file_obj:
                s3.upload_fileobj(file_obj, AWS_BUCKET_NAME, str(file_obj))
                setattr(upload, field, f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{file_obj}")

        upload.save()
        context = {
            "data": upload,
            "all_data": all_data,
            "s3_url": upload.photo or upload.video or upload.recording,
            "is_name": is_name,
            "is_comments": is_comments,
            "imei": imei,
        }
        return render(request, "base/output.html", context)

    except Exception as e:
        logger.error("Error uploading file to S3: %s", str(e))
        return render(request, "base/index2.html", {"imei": imei})

def ViewData(request, slug):
    upload = get_object_or_404(UploadData, slug=slug)
    return render(request, "base/view.html", {"data": upload})

class SetAssignedFlag(APIView):
    def post(self, request, slug):
        upload = get_object_or_404(UploadData, slug=slug)
        upload.is_assigned = True
        upload.save()
        return Response({"Message": "Tag Assigned Successfully"}, status=status.HTTP_200_OK)