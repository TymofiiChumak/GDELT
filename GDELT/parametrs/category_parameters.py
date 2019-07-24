import pandas as pd
from .parameter import Parameter
from .text_parameter import TextParameter
from ..utils.utils import Utils


class GenericCategoryParameter(TextParameter):
    """
    Generic type for category parameters.
    Is needed to set id_to_name_mapping attribute (dynamically, or by inheritance).
    id_to_name_mapping - pandas Series with values witch be displayed and indexes with be returned.
    i.e. if index is "US" and value is "United States", user must write "United states"
    but "US" will be returned
    """
    _allow_multiple = False
    _allow_all = False
    _allow_null = False

    def __init__(self, value):
        if self._allow_multiple:
            values = filter(lambda x: x != "", value.split(';'))
            values = map(lambda val: self.id_to_name_mapping[self.id_to_name_mapping == val.strip()].index[0], values)
            Parameter.__init__(self, list(values))
        else:
            Parameter.__init__(self, self.id_to_name_mapping[self.id_to_name_mapping == value.strip()].index[0])

    @classmethod
    def get_field_code(cls, params, default_value):
        param_id, label = params
        datalist_id = param_id + "_list"
        datalist = cls._get_datalist(cls.id_to_name_mapping.unique(), datalist_id)
        multiple_data = 'data-multiple' if cls._allow_multiple else ''
        drop_down = 'dropdown-input' if cls.id_to_name_mapping.shape[0] < 10 else ''
        test_form_field = """
        {datelist}
        <div class="form-group">
            <label for="{param_id}" style="width:100%; vertical-align: middle;"> {label} </label>
            <input type="text" 
                   class="form-control param awesomplete {multiple_data} {drop_down}" 
                   id="{param_id}" 
                   value="{default_value}" 
                   list="{datelist_id}"/>
        </div>""".format(param_id=param_id,
                         label=label,
                         default_value=default_value,
                         datelist_id=datalist_id,
                         datelist=datalist,
                         multiple_data=multiple_data,
                         drop_down=drop_down)
        return test_form_field

    @classmethod
    def get_value_from_default(cls, value):
        if cls._allow_multiple:
            names = map(lambda val: cls.id_to_name_mapping[val], value)
            return ';'.join(names) + ';'
        else:
            return cls.id_to_name_mapping[value]

    @classmethod
    def check_params(cls, value):
        def check(val):
            assert val.strip() in cls.id_to_name_mapping.values, "Wrong value"
            return True
        if cls._allow_multiple:
            return all(map(check, filter(lambda x: x != "", value.split(';'))))
        else:
            return check(value)

    @classmethod
    def allow_null(cls, null_name="None", null_index="None"):
        """
        Adds null value to possible values of field.
        Don't change behaviour of base class.
        Handling of this value must be considered in calling function.
        :param null_name: null value to be displayed
        :param null_index: null value to be returned
        :return: new class with additional "null" value inserted to
        id_to_name_mapping attribute
        """
        new_id_to_name_mapping = cls.id_to_name_mapping.copy()
        new_id_to_name_mapping.at[null_index] = null_name
        return type(cls.__name__ + "_null",
                    (cls,),
                    {
                        "id_to_name_mapping": new_id_to_name_mapping,
                        "null_name": null_name,
                        "null_index": null_index,
                        "_allow_all": True,
                    })

    @classmethod
    def allow_all(cls, all_name="All", all_index="All"):
        """
        Adds all value to possible values of field.
        Don't change behaviour of base class.
        Handling of this value must be considered in calling function.
        :param all_name: all value to be displayed
        :param all_index: all value to be returned
        :return: new class with additional "all" value inserted to
        id_to_name_mapping attribute
        """
        new_id_to_name_mapping = cls.id_to_name_mapping.copy()
        new_id_to_name_mapping.at[all_index] = all_name
        return type(cls.__name__ + "_all",
                    (cls,),
                    {
                        "id_to_name_mapping": new_id_to_name_mapping,
                        "all_name": all_name,
                        "all_index": all_index,
                        "_allow_all": True,
                    })

    @classmethod
    def allow_multiple(cls):
        """
        Allows multiple values inserted into param filed.
        After applying "value" attribute becomes list of values.
        Values in input field must be divided by ";"
        :return:
        """
        return type(cls.__name__ + "_mul",
                    (cls,),
                    {"_allow_multiple": True})

    @staticmethod
    def _get_datalist(elements, name):
        """
        "private" method to create html datalist in propose of autocomplete
        :param elements: list of string values
        :param name: id of field
        :return: html datalist node
        """
        datalist = """<datalist id="{}">""".format(name)
        for element in elements:
            datalist += "<option>" + str(element) + "</option>"
        datalist += "</datalist>"
        return datalist


CameoCountryParameter = type("CameoCountryParameter",
                             (GenericCategoryParameter,),
                             {"id_to_name_mapping": Utils().get_cameo_country_id_to_name_mapping()})


CameoEthnicParameter = type("CameoEthnicParameter",
                            (GenericCategoryParameter,),
                            {"id_to_name_mapping": Utils().get_cameo_ethnic_id_to_name_mapping()})


CameoKnownGroupParameter = type("CameoKnownGroupParameter",
                                (GenericCategoryParameter,),
                                {"id_to_name_mapping": Utils().get_cameo_knowngroups_id_to_name_mapping()})


CameoReligionParameter = type("CameoReligionParameter",
                              (GenericCategoryParameter,),
                              {"id_to_name_mapping": Utils().get_cameo_religion_id_to_name_mapping()})


CameoEventcodeBaseParameter = type("CameoReligionParameter",
                                   (GenericCategoryParameter,),
                                   {"id_to_name_mapping": Utils().get_cameo_base_eventcodes_id_to_name_mapping()})


CameoEventcodeParameter = type("CameoReligionParameter",
                               (GenericCategoryParameter,),
                               {"id_to_name_mapping": Utils().get_cameo_eventcodes_id_to_name_mapping()})


FipsCountryParameter = type("FipsCountryParameter",
                            (GenericCategoryParameter,),
                            {"id_to_name_mapping": Utils().get_fips_country_id_to_name_mapping()})


quad_class_mapping = pd.Series(
    ['Verbal Cooperation', 'Material Cooperation', 'Verbal Conflict', 'Material Conflict'],
    index=[1, 2, 3, 4]
)

QuadClassParameter = type("QuadClassParameter",
                          (GenericCategoryParameter,),
                          {"id_to_name_mapping": quad_class_mapping})


# FipsRegionParameter = type("FipsRegionParameter",
#                            (GenericCategoryParameter,),
#                            {"id_to_name_mapping": Utils().get_fips_region_id_to_name_mapping()})


actor_to_id_mapping = pd.Series(['Actor 1', 'Actor 2'], index=[1, 2])
ActorTypeParameter = type("ActorTypeParameter",
                          (GenericCategoryParameter,),
                          {"id_to_name_mapping": actor_to_id_mapping})


type_to_id_mapping = pd.Series(['Event Count',
                                'Average Tone',
                                'Sum Mentions',
                                'Average Goldstein scale'],
                               index=[1, 2, 3, 4])
TargetTypeParameter = type("TragetTypeParameter",
                          (GenericCategoryParameter,),
                          {"id_to_name_mapping": type_to_id_mapping})