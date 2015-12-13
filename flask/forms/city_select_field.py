__all__ = [b"CitySelectField"]


def CitySelectField(*args, **kwargs):
	# This code fails on migration:
    choices = [(city.id, city.name, entity_to_dict(city)) for city in db.session.query(City).all()]

    for k, v, d in choices:
        for quota, values in d["quota"].items():
            sm = sum(values.values())
            for k in values:
                values[k] /= sm

    return SelectFieldWithOptionData(*args, choices=choices, coerce=int, **kwargs)
