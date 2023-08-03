
from rest_framework import status


def create_or_delete_relation(model, user, subject, request):
    field_names = [field.name for field in model._meta.get_fields()]
    user_field = field_names[1]
    subject_field = field_names[2]
    if request.method == 'POST':
        try:
            model.objects.get(**{user_field: user, subject_field: subject})
            response = {
                'string': {'detail': 'relation already exists'},
                'status': status.HTTP_400_BAD_REQUEST,
            }
            return response
        except model.DoesNotExist:
            instance = model.objects.create(
                **{user_field: user, subject_field: subject}
            )
            response = {
                'string': {'detail': 'relation created'},
                'status': status.HTTP_200_OK,
                'instance': instance,
            }
            return response
    if request.method == 'DELETE':
        try:
            instance = model.objects.get(
                **{user_field: user, subject_field: subject}
            )
            instance.delete()
            response = {
                'string': {'detail': 'relation deleted'},
                'status': status.HTTP_204_NO_CONTENT,
            }
            return response
        except model.DoesNotExist:
            response = {
                'string': {'errors': 'relation does not exist'},
                'status': status.HTTP_400_BAD_REQUEST,
            }
            return response
