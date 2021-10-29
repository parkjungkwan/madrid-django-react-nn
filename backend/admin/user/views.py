from django.http import JsonResponse
from icecream import ic
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser

from admin.user.models import User
from admin.user.serializers import UserSerializer

@api_view(['GET','POST','PUT'])
@parser_classes([JSONParser])
def users(request):
    if request.method == 'GET':
        all_users = User.objects.all()
        serializer = UserSerializer(all_users, many=True)
        return JsonResponse(data = serializer, safe = False)
    elif request.method == 'POST':
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'result' : f'Welcome, {serializer.data.get("name")}'}, status=201)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PUT':

        return None

@api_view(['DELETE'])
def remove(request, id):
    pass

@api_view(['POST'])
def login(request):
    print('+++++++ try 밖에 있음 ++++++++')
    try:
        print('*' * 50)
        print('try 에 들어옴')
        loginUser = request.data
        print('*' * 100)
        ic(loginUser)
        serializer = UserSerializer(loginUser, many=True)
        return JsonResponse(data=serializer, safe=False)
    except User.DoesNotExist:
        print('*' * 50)
        print('에러 발생')
        return JsonResponse(data=serializer, safe=False)




