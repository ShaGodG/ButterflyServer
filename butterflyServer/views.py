import json
import os

from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from textblob.formats import JSON

from butterflyServer.label_image import get_label
from django.views.decorators.csrf import csrf_exempt


class FileForm(forms.Form):
    username = forms.CharField()
    file = forms.FileField()  # for creating file input


def handle_uploaded_file(f, username):
    directory = 'static/upload/' + username + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return directory + f.name

@csrf_exempt
def getFile(request):
    if request.method == 'POST':
        fileForm = FileForm(request.POST, request.FILES)
        if fileForm.is_valid():
            file_path = handle_uploaded_file(request.FILES['file'], request.POST['username'])
            result_dict = get_label({
                'labels': 'butterflyServer/output_labels.txt',
                'graph': 'butterflyServer/output_graph.pb',
                'input_layer': 'Placeholder',
                'image': file_path,
                'output_layer': 'final_result'
            })
            result_json = []
            for each in result_dict:
                a = {}
                a['name'] = each
                a['value'] = result_dict[each]
                # print(a,'a')
                result_json.append(a)

            sorted_result = sorted(result_json, key = lambda i: -i['value'])
            print(file_path,  sorted_result)
            if(float(sorted_result[0]['value'])<0.30):
                return HttpResponse('error')
            else:
                return HttpResponse(json.dumps(str(sorted_result[0]['name'])))
        return HttpResponse("false")
    else:
        fileForm = FileForm()
        return render(request, "index.html", {'form': fileForm})
