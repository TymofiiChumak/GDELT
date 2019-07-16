from .parameter import ParameterUtil, Parameter
from .text_parameter import TextParameter
from ..utils.utils import Utils


class GenericCategoryParameter(TextParameter):
    id_to_name_mapping = Utils().get_cameo_country_id_to_name_mapping()

    def __init__(self, value):
        Parameter.__init__(self, self.id_to_name_mapping[self.id_to_name_mapping == value].index[0])

    @classmethod
    def get_field_code(cls, params, default_value):
        param_id, label = params
        datalist_id = param_id + "_list"
        datalist = ParameterUtil.get_datalist(cls.id_to_name_mapping.unique(), datalist_id)
        test_form_field = """
        <div class="form-group">
            <label for="{0}"> {1} </label>
            <input type="text" class="form-control param awesomplete" id="{0}" value="{2}" list="{3}">
            {4}
        </div>""".format(param_id, label, default_value, datalist_id, datalist)
        return test_form_field

    @classmethod
    def get_value_from_default(cls, value):
        print(cls.id_to_name_mapping[value])
        return cls.id_to_name_mapping[value]

    @classmethod
    def check_params(cls, value):
        assert value in cls.id_to_name_mapping.values, "Wrong value"
        return True


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
                                   {"id_to_name_mapping": Utils().get_cameo_eventcodes_id_to_base_mapping()})


CameoEventcodeParameter = type("CameoReligionParameter",
                               (GenericCategoryParameter,),
                               {"id_to_name_mapping": Utils().get_cameo_eventcodes_id_to_name_mapping()})


FipsCountryParameter = type("FipsCountryParameter",
                            (GenericCategoryParameter,),
                            {"id_to_name_mapping": Utils().get_fips_country_id_to_name_mapping()})


# FipsRegionParameter = type("FipsRegionParameter",
#                            (GenericCategoryParameter,),
#                            {"id_to_name_mapping": Utils().get_fips_region_id_to_name_mapping()})

