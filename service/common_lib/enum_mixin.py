class EnumMixin(object):
    """
    Adds helper methods to an enum class

    A key use is for defining a Django model field's choices list.  Django choices lists take in a list of (value, name)
    tuples, where `value` is the value stored in the database, and `name` is the user-friendly description, used in the
    admin UI forms.  Some enums are define with the name as the DB value, but some use the value as the DB value, as it
    couldn't be used as a name (such as a number).

    When used as a choices list, the name is used as the display name, and the value is the value stored in the db.
    This allows the value to be numeric, which wouldn't be possible if the enum name was used as the db value, but
    means that you can't define an enum with friendly display text, containing spaces, since that isn't a valid
    enum name.
    """

    @classmethod
    def value_name_list(cls):
        """
        Use the enum field name as the user-friendly description, and the value as the db value

        This is useful for defining a model field's choices when the db value is a number, as you could not use the enum
        field name for this.
        :return: list[tuple(str/int, str)]
        """
        return [(c.value, c.name) for c in cls]

    @classmethod
    def name_value_list(cls):
        """
        Use the enum field name as the db value, and the enum value as the user-fiendly description

        This is useful for defining a model field's choices when the db value is a string, as you can store the enum
        name in the db, and the value can be a more readable string.
        :return: list[tuple(str/int, str)]
        """
        return [(c.name, c.value) for c in cls]

    @classmethod
    def values(cls):
        """Return a list of the values of the enum.  Useful for a choices list for a schema."""
        return [c.value for c in cls]

    @classmethod
    def all(cls):
        """Return a list of all enum options."""
        return [c for c in cls]

    @classmethod
    def names(cls):
        """Return a list of the names of the enum options."""
        return [c.name for c in cls]

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def name_from_value(cls, value) -> str:
        """Return the enum name with the specified value, or null if not found in the enum class"""
        return cls(value).name if cls.has_value(value) else None

    @classmethod
    def value_from_name(cls, name) -> str:
        """Return the enum value with the specified name, or null if not found in the enum class"""
        return cls[name].value if hasattr(cls, name) else None
