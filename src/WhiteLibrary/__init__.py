import clr
import os
from robot.api import logger   # noqa: F401
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'TestStack.White.dll')
clr.AddReference('System')
clr.AddReference(dll_path)
from System.Windows.Automation import AutomationElement   # noqa: E402
from TestStack.White.UIItems.Finders import SearchCriteria   # noqa: E402
from WhiteLibrary.keywords import ApplicationKeywords, KeyboardKeywords, WindowKeywords, ScreenshotKeywords   # noqa: E402
from WhiteLibrary.keywords.items import (ButtonKeywords,
                            LabelKeywords,
                            ListKeywords,
                            MenuKeywords,
                            ProgressbarKeywords,
                            SliderKeywords,
                            TabKeywords,
                            TreeKeywords,
                            TextBoxKeywords,
                            UiItemKeywords)   # noqa: E402
from WhiteLibrary.keywords.robotlibcore import DynamicCore   # noqa: E402
from WhiteLibrary import version   # noqa: E402


STRATEGIES = {"id": "ByAutomationId",
              "text": "ByText",
              "index": "Indexed"}


class WhiteLibrary(DynamicCore):
    """WhiteLibrary is a Robot Framework library for automating Windows GUI.
    It is a wrapper for [https://github.com/TestStack/White | TestStack.White].

    = Applications and windows =
    

    = Item locators =
    Keywords that access UI items (e.g. `Click Button`) use a ``locator`` argument.
    The locator consists of a locator prefix that specifies the search criteria, and the locator value.

    | = Search criteria = | = Prefix =              | = Description =                 |
    | By AutomationID     | id (or no prefix)       | Search by AutomationID. If no prefix is given, the item is searched by AutomationID by default. |
    | By text             | text                    | Search by exact item text/name. |
    | Indexed             | index                   | Search by item index.           |
    | By native property  | property name, e.g. ClassNameProperty  | Search by native property. |

    Examples:

    | Click Button | myButton         | # clicks button by its AutomationID |
    | Click Button | id=myButton      | # clicks button by its AutomationID |
    | Click Button | text=Click here! | # clicks button by the button text  |
    | Click Button | index=2          | # clicks button whose index is 2    |
    """
    ROBOT_LIBRARY_VERSION = version.VERSION
    ROBOT_LIBRARY_SCOPE = "Global"
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.window = None
        self.screenshooter = None
        self.ROBOT_LIBRARY_LISTENER = self
        self.screenshot_type = 'desktop'
        self.screenshots_enabled = True
        self.libraries = [ApplicationKeywords(self),
                          ButtonKeywords(self),
                          KeyboardKeywords(self),
                          LabelKeywords(self),
                          ListKeywords(self),
                          MenuKeywords(self),
                          ProgressbarKeywords(self),
                          SliderKeywords(self),
                          TabKeywords(self),
                          TextBoxKeywords(self),
                          TreeKeywords(self),
                          UiItemKeywords(self),
                          WindowKeywords(self),
                          ScreenshotKeywords(self)]
        DynamicCore.__init__(self, self.libraries)

    def _get_typed_item_by_locator(self, item_type, locator):
        search_criteria = self._get_search_criteria(locator)
        return self.window.Get[item_type](search_criteria)

    def _get_item_by_locator(self, locator):
        search_criteria = self._get_search_criteria(locator)
        return self.window.Get(search_criteria)

    def _get_search_criteria(self, locator):
        if "=" not in locator:
            locator = "id=" + locator
        try:
            search_method, search_params = self._get_search_method(locator)
        except AttributeError as e:
            raise ValueError("Invalid locator prefix. " + e.message)

        method = getattr(SearchCriteria, search_method)
        logger.debug("Search method: {}, parameters: {}".format(method, search_params))
        return method(*search_params)

    def _get_search_method(self, locator):
        search_strategy, locator_value = locator.split("=")
        if search_strategy == "index":
            locator_value = int(locator_value)

        if search_strategy in STRATEGIES:
            search_method = STRATEGIES[search_strategy]
            search_params = (locator_value,)
        else:
            search_method = "ByNativeProperty"
            property_name = getattr(AutomationElement, search_strategy)
            search_params = (property_name, locator_value)

        return search_method, search_params

    def _end_keyword(self, name, attrs):
        if attrs['status'] == 'FAIL':
            if self.screenshot_type == 'desktop' and self.screenshots_enabled:
                self.screenshooter.take_desktop_screenshot()

    def _contains_string_value(self, expected, actual, case_sensitive=True):
        expected_value = expected if not case_sensitive else expected.upper()
        actual_value = actual if not case_sensitive else actual.upper()

        if expected_value not in actual_value:
            raise AssertionError("Expected value {} not found in {}".format(expected, actual))

    def _verify_string_value(self, expected, actual, case_sensitive=True):
        expected_value = expected if not case_sensitive else expected.upper()
        actual_value = actual if not case_sensitive else actual.upper()

        if expected_value != actual_value:
            raise AssertionError("Expected value {}, but found {}".format(expected, actual))

    def _verify_value(self, expected, actual):
        if expected != actual:
            raise AssertionError("Expected value {}, but found {}".format(expected, actual))
