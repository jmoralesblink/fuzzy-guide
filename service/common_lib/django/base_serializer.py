from rest_framework.serializers import Serializer


class BaseSerializer(Serializer):
    """
    A base serializer that isn't tied to a model, and implements required functions to silence warnings

    All serializers should inherit from this class to help ensure consistency.

    You can set select_related and prefetch_related when defining the serializer, and an BaseAPIView will include those
    in it's default queryset if the serializer is defined as serializer_class for that view.

        class BasicReadOnlyPrescriptionFillSerializer(BaseSerializer):
            select_related = ("drug", "drug__med_name")
            id = IntegerField()
    """

    def create(self, validated_data):
        """
        Must be implemented when reading in data as input, and de-serializing it
        :param validated_data:
        :return:
        """
        # Example:
        # new_object = Patient(**validated_data)
        # new_object.custom_field = validated_data.get('some_value')
        # return new_object
        pass

    def update(self, instance, validated_data):
        """
        Not used, since the serializer should not touch an existing instance directly
        """
        pass
