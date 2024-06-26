import importlib, inspect
import unittest
from unittest import mock
from unittest.mock import patch, MagicMock

from sagemaker_core.generated.resources import Base, Action

from sagemaker_core.code_injection.codec import pascal_to_snake, snake_to_pascal

from sagemaker_core.generated.utils import SageMakerClient


class ResourcesTest(unittest.TestCase):
    MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME = {}
    SHAPE_CLASSES_BY_SHAPE_NAME = {}
    PARAM_CONSTANTS_BY_TYPE = {
        "str": "Random-String",
        "int": 0,
        "List": [],
        "Dict": {},
        "bool": False,
    }

    def setUp(self) -> None:
        for name, cls in inspect.getmembers(
            importlib.import_module("sagemaker_core.generated.resources"), inspect.isclass
        ):
            if cls.__module__ == "sagemaker_core.generated.resources":
                if hasattr(cls, "get") and callable(cls.get):
                    self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME[name] = (
                        self._get_required_parameters_for_function(cls.get)
                    )

        for shape_name, shape_cls in inspect.getmembers(
            importlib.import_module("sagemaker_core.generated.shapes"), inspect.isclass
        ):
            if shape_cls.__module__ == "sagemaker_core.generated.shapes":
                self.SHAPE_CLASSES_BY_SHAPE_NAME[shape_name] = shape_cls

    @patch("sagemaker_core.generated.resources.transform")
    @patch("boto3.session.Session")
    def test_resources(self, session, mock_transform):
        report = {"Create": 0, "Update": 0, "Get": 0, "Get_all": 0, "Refresh": 0, "Delete": 0}
        resources = set()
        client = SageMakerClient(session=session).client
        for name, cls in inspect.getmembers(
            importlib.import_module("sagemaker_core.generated.resources"), inspect.isclass
        ):
            if cls.__module__ == "sagemaker_core.generated.resources":
                print_string = f"Running the following tests for resource {name}: "
                resources.add(name)
                if hasattr(cls, "get") and callable(cls.get):
                    function_name = f"describe_{pascal_to_snake(name)}"
                    input_args = self._get_required_parameters_for_function(cls.get)
                    pascal_input_args = self._convert_dict_keys_into_pascal_case(input_args)
                    with patch.object(
                        client, function_name, return_value=pascal_input_args
                    ) as mock_method:
                        mock_transform.return_value = (
                            self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(name)
                        )
                        input_args = self._get_required_parameters_for_function(cls.get)
                        pascal_input_args = self._convert_dict_keys_into_pascal_case(input_args)
                        cls.get(**input_args)
                        mock_method.assert_called_once()
                        self.assertLessEqual(
                            pascal_input_args.items(),
                            mock_method.call_args[1].items(),
                            f"Get call verification failed for {name}",
                        )
                    report["Get"] = report["Get"] + 1
                    print_string = print_string + " Get"

                    if hasattr(cls, "get_all") and callable(cls.get_all):
                        function_name = self._get_function_name_for_list(pascal_to_snake(name))
                        get_function_name = f"describe_{pascal_to_snake(name)}"
                        summary = self._convert_dict_keys_into_pascal_case(
                            self._get_required_parameters_for_function(cls.get)
                        )
                        if (
                            name == "DataQualityJobDefinition"
                            or name == "ModelBiasJobDefinition"
                            or name == "ModelQualityJobDefinition"
                            or name == "ModelExplainabilityJobDefinition"
                        ):
                            custom_key_mapping = {
                                "JobDefinitionName": "MonitoringJobDefinitionName",
                                "JobDefinitionArn": "MonitoringJobDefinitionArn",
                            }
                            summary = {custom_key_mapping.get(k, k): v for k, v in summary.items()}
                        summary_response = {
                            f"{name}Summaries": [summary],
                            "JobDefinitionSummaries": [summary],
                            f"{name}SummaryList": [summary],
                            f"{name}s": [summary],
                        }
                        with patch.object(
                            client, function_name, return_value=summary_response
                        ) as mock_method:
                            mock_transform.return_value = (
                                self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(name)
                            )
                            with patch.object(
                                client, get_function_name, return_value={}
                            ) as mock_get_method:
                                input_args = self._get_required_parameters_for_function(cls.get_all)
                                pascal_input_args = self._convert_dict_keys_into_pascal_case(
                                    input_args
                                )
                                cls.get_all(**input_args).__next__()
                                mock_method.assert_called_once()
                                mock_get_method.assert_called_once()
                                self.assertLessEqual(
                                    pascal_input_args.items(),
                                    mock_method.call_args[1].items(),
                                    f"Get All call verification failed for {name}",
                                )
                        report["Get_all"] = report["Get_all"] + 1
                        print_string = print_string + " Get_All"

                if hasattr(cls, "refresh") and callable(cls.refresh):
                    function_name = f"describe_{pascal_to_snake(name)}"
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    with patch.object(client, function_name, return_value={}) as mock_method:
                        class_instance = cls(**self._get_required_parameters_for_function(cls.get))
                        input_args = self._get_required_parameters_for_function(cls.refresh)
                        pascal_input_args = self._convert_dict_keys_into_pascal_case(input_args)
                        class_instance.refresh(**input_args)
                        mock_method.assert_called_once()
                        self.assertLessEqual(
                            pascal_input_args.items(), mock_method.call_args[1].items()
                        )
                    report["Refresh"] = report["Refresh"] + 1
                    print_string = print_string + " Refresh"

                    if hasattr(cls, "delete") and callable(cls.delete):
                        function_name = f"delete_{pascal_to_snake(name)}"
                        mock_transform.return_value = (
                            self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(name)
                        )
                        with patch.object(client, function_name, return_value={}) as mock_method:
                            class_instance = cls(
                                **self._get_required_parameters_for_function(cls.get)
                            )
                            input_args = self._get_required_parameters_for_function(cls.delete)
                            pascal_input_args = self._convert_dict_keys_into_pascal_case(input_args)
                            class_instance.delete(**input_args)
                            mock_method.assert_called_once()
                            self.assertLessEqual(
                                pascal_input_args.items(),
                                mock_method.call_args[1].items(),
                                f"Delete call verification failed for {name}",
                            )
                        report["Delete"] = report["Delete"] + 1
                        print_string = print_string + " Delete"

                    if hasattr(cls, "create") and callable(cls.create):
                        get_function_name = f"describe_{pascal_to_snake(name)}"
                        create_function_name = f"create_{pascal_to_snake(name)}"
                        input_args = self._get_required_parameters_for_function(cls.create)
                        pascal_input_args = self._convert_dict_keys_into_pascal_case(input_args)
                        with patch.object(
                            client,
                            create_function_name,
                            return_value=self._convert_dict_keys_into_pascal_case(
                                self._get_required_parameters_for_function(cls.get)
                            ),
                        ) as mock_create_method:
                            with patch.object(
                                client, get_function_name, return_value={}
                            ) as mock_get_method:
                                cls.create(**input_args)
                                mock_create_method.assert_called_once()
                                mock_get_method.assert_called_once()
                                self.assertLessEqual(
                                    Base._serialize(
                                        Base.populate_chained_attributes(
                                            operation_input_args=pascal_input_args,
                                            resource_name=name,
                                        )
                                    ).items(),
                                    mock_create_method.call_args[1].items(),
                                    f"Create call verification failed for {name}",
                                )
                        report["Create"] = report["Create"] + 1
                        print_string = print_string + " Create"

                    if hasattr(cls, "update") and callable(cls.update):
                        get_function_name = f"describe_{pascal_to_snake(name)}"
                        update_function_name = f"update_{pascal_to_snake(name)}"
                        with patch.object(
                            client,
                            update_function_name,
                            return_value=self._convert_dict_keys_into_pascal_case(
                                self._get_required_parameters_for_function(cls.get)
                            ),
                        ) as mock_update_method:
                            with patch.object(
                                client, get_function_name, return_value={}
                            ) as mock_get_method:
                                input_args = self._get_required_parameters_for_function(cls.update)
                                pascal_input_args = self._convert_dict_keys_into_pascal_case(
                                    input_args
                                )
                                class_instance = cls(
                                    **self._get_required_parameters_for_function(cls.get)
                                )
                                class_instance.update(**input_args)
                                mock_update_method.assert_called_once()
                                mock_get_method.assert_called_once()
                                self.assertLessEqual(
                                    Base._serialize(pascal_input_args).items(),
                                    mock_update_method.call_args[1].items(),
                                    f"Update call verification failed for {name}",
                                )
                        report["Update"] = report["Update"] + 1
                        print_string = print_string + " Update"
                print(print_string)

        total_tests = sum(report.values())

        print("Total Tests Executed = ", total_tests)
        print("Total Resources Executed For = ", len(resources))

        for method, count in report.items():
            print(f"Total Tests Executed for {method} = {count}")

    def _get_function_name_for_list(self, resource_name):
        if resource_name == "code_repository":
            return "list_code_repositories"
        return f"list_{resource_name}s"

    def _convert_dict_keys_into_pascal_case(self, input_args: dict):
        return {self._convert(key): val for key, val in input_args.items()}

    def _convert(self, string: str):
        if string == "auto_ml_job_name":
            return "AutoMLJobName"
        return snake_to_pascal(string)

    def _get_required_parameters_for_function(self, func) -> dict:
        params = {}
        for key, val in inspect.signature(func).parameters.items():
            attribute_type = str(val)
            if (
                key != "session"
                and key != "region"
                and "Optional" not in attribute_type
                and key != "self"
                and "utils.Unassigned" not in attribute_type
            ):
                if "str" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["str"]
                elif "int" in attribute_type or "float" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["int"]
                elif "bool" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["bool"]
                elif "List" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["List"]
                else:
                    shape = attribute_type.split(".")[-1]
                    params[key] = self._generate_test_shape(
                        self.SHAPE_CLASSES_BY_SHAPE_NAME.get(shape)
                    )
        return params

    def _generate_test_shape(self, shape_cls):
        params = {}
        if shape_cls == None:
            return None
        for key, val in inspect.signature(shape_cls).parameters.items():
            attribute_type = str(val.annotation)
            if "Optional" not in attribute_type and "utils.Unassigned" not in str(val):
                if "List[str]" in attribute_type:
                    params[key] = ["Random-String"]
                elif "List" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["List"]
                elif "Dict" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["Dict"]
                elif "bool" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["bool"]
                elif "str" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["str"]
                elif "int" in attribute_type or "float" in attribute_type:
                    params[key] = self.PARAM_CONSTANTS_BY_TYPE["int"]
                else:
                    shape = str(val).split(".")[-1]
                    params[key] = self._generate_test_shape(
                        self.SHAPE_CLASSES_BY_SHAPE_NAME.get(shape)
                    )

        return shape_cls(**params)