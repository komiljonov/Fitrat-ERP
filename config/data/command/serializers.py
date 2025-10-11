class BaseSerializer:
    """
    Mixin for DRF serializers to support:
      - include_only / remove_fields kwargs at init-time
      - classmethods .only(...) / .remove(...) that return a subclass with presets
    """

    # class-level presets (set by the factories below)
    _preset_include_only: set[str] | None = None
    _preset_remove_fields: set[str] | None = None

    def __init__(self, *args, **kwargs):
        # runtime kwargs
        fields_to_remove: list[str] | None = kwargs.pop("remove_fields", None)
        include_only: list[str] | None = kwargs.pop("include_only", None)

        # merge with class-level presets from factories
        preset_only = getattr(self.__class__, "_preset_include_only", None)
        preset_remove = getattr(self.__class__, "_preset_remove_fields", None)

        # compute effective filters
        eff_only = set(include_only or []) | (preset_only or set())
        eff_remove = set(fields_to_remove or []) | (preset_remove or set())

        # guardrail: cannot use both at the same time
        if eff_only and eff_remove:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' simultaneously (including presets)."
            )

        super().__init__(*args, **kwargs)

        # apply filters
        if eff_only:
            allowed = eff_only
            for field_name in set(self.fields) - allowed:
                self.fields.pop(field_name, None)
        elif eff_remove:
            for field_name in eff_remove:
                self.fields.pop(field_name, None)

    # ---- factories that return a subclass (usable as serializer_class) ----
    @classmethod
    def only(cls, *fields: str):
        """
        Returns a subclass of `cls` with include_only preset.
        Use directly in views as serializer_class = MySerializer.only("id", "email")
        """
        name = f"{cls.__name__}Only__{'_'.join(fields) if fields else 'None'}"
        return type(
            name,
            (cls,),
            {"_preset_include_only": set(fields), "_preset_remove_fields": None},
        )

    @classmethod
    def remove(cls, *fields: str):
        """
        Returns a subclass of `cls` with remove_fields preset.
        Use directly in views as serializer_class = MySerializer.remove("password")
        """
        name = f"{cls.__name__}Remove__{'_'.join(fields) if fields else 'None'}"
        return type(
            name,
            (cls,),
            {"_preset_include_only": None, "_preset_remove_fields": set(fields)},
        )
