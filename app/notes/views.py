from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import UserModel, Notes
from .permissions import IsAdmin, IsNotBanned, IsOwnerOrAdmin, IsSameUserOrAdmin
from .serializers import NotesSerializer, UserSerializer
from rest_framework import filters


# Create your views here.
class CreateAdminNotes(generics.CreateAPIView):
    serializer_class = NotesSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdmin, IsNotBanned,)

    """
        Only used by the administrator to create
        notes to any users
    """

    def post(self, request, format=None):
        """
            Post request to create notes when you are an administrator
            :param self: The class itself
            :param request: The post request
            :param format: The format of the request
        """
        try:
            owner_email = request.data['owner']
            notes_owner = UserModel.objects.get(email=owner_email)
            notes = Notes(title=request.data['title'], description=request.data['body'], owner=notes_owner)
            notes.save()
            serializer = NotesSerializer(notes)
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'errors': 'Fields required: title, description and owner'})


class ListNotes(generics.ListCreateAPIView,generics.ListAPIView):
    """
        List all the notes present inside the database
        also allows POST request to create some
    """
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    permission_classes = (permissions.IsAuthenticated, IsNotBanned,)

    def perform_create(self, serializer):
        """
            Override the perform_create from the generic
            serializers.
            :param self: Class
            :param serializer: serializer used to perform actions
        """
        serializer.save(owner=self.request.user)


class DestroyAPIView(generics.RetrieveDestroyAPIView):
    """
    Concrete view for deleting a model instance.
    """
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin, IsNotBanned,)


class UpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Concrete view for updating a model instance.
    """
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdmin, IsNotBanned,)


class ListUser(generics.ListCreateAPIView):
    """
        List all users from the database
        also allows POST request to create some
    """
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin, IsNotBanned,)


class DetailUser(generics.RetrieveUpdateDestroyAPIView):
    """
        Detail the specific user from the database
        also allows the update and the destroy of this
        specific user
    """
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsSameUserOrAdmin, IsNotBanned,)


class FilterAPIView(generics.ListCreateAPIView):
    search_fields = ['tags']
    filter_backends = (filters.SearchFilter,)
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer

