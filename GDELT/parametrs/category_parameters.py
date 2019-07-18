import numpy as np
from .parameter import ParameterUtil, Parameter
from .text_parameter import TextParameter
from ..utils.utils import Utils


class GenericCategoryParameter(TextParameter):
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
        datalist = ParameterUtil.get_datalist(cls.id_to_name_mapping.unique(), datalist_id)
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
        return type(cls.__name__ + "_mul",
                    (cls,),
                    { "_allow_multiple": True})


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


QuadClassParameter = type("QuadClassParameter",
                          (GenericCategoryParameter,),
                          {"id_to_name_mapping": Utils().get_quad_class_mapping()})


# FipsRegionParameter = type("FipsRegionParameter",
#                            (GenericCategoryParameter,),
#                            {"id_to_name_mapping": Utils().get_fips_region_id_to_name_mapping()})

