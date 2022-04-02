from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # <-- Here

import json

class HelloView(APIView):
    permission_classes = (IsAuthenticated,)             # <-- And here

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

class RegisterMultipleNodes(APIView):
    permission_classes = (IsAuthenticated,)             # <-- And here

    def post(self, request):
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        print(json_data)
        content = {'message': 'Hello, World!'}
        return Response(content)