import cern_sso

from zeep import Client
from zeep.transports import Transport

from dbconstants import WSDL
# from KerberosTicketGenerator import AttemptGenerateKerberosTicket

try:
    # AttemptGenerateKerberosTicket()
    cookies = cern_sso.krb_sign_on(WSDL)
    transport = Transport(cache=False)
    transport.session.cookies.update(cookies)
    client = Client(WSDL, transport=transport)
except Exception as e:
    raise


class DBRequest:
    def __init__(self, executeImmediately=True, **kwargs):
        self.RequestInfo = kwargs
        self.validate()
        if executeImmediately:
            self.ExecuteRequest()

    def validate(self):
        """
        Throw key and type errors as appropriate
        """
        pass

    def _checkResponseError(self):
        errorCode = getattr(self.Response, "ErrorCode", 0)
        errorMessage = getattr(self.Response, "ErrorMessage", 'OK')

        try:
            assert errorCode == 0
            assert errorMessage == 'OK'
        except AssertionError:
            raise AssertionError(errorMessage)

    def ExecuteRequest(self):
        self.Response = self.Request(**self.RequestInfo)
        self._checkResponseError()


class DBRemoveRequest(DBRequest):
    def validate(self):
        int(self.RequestInfo['ID'])


################################################################
# Wrap all functions defined at
# https://test-alucmsapi.web.cern.ch/AlucmswebAPI.asmx
# Grouped by updates, then reads, mostly alphabetical
################################################################
class ActivityAttachmentCreate(DBRequest):
    Request = getattr(client.service, 'ActivityAttachmentCreate')

    def validate(self):
        int(self.RequestInfo['activityID'])
        int(self.RequestInfo['attachmentCategoryID'])
        self.RequestInfo['file']
        self.RequestInfo['fileName']
        int(self.RequestInfo['userID'])


class ActivityAttachmentRemove(DBRemoveRequest):
    Request = getattr(client.service, 'ActivityAttachmentRemove')


class ActivityComponentAssign(DBRequest):
    Request = getattr(client.service, 'ActivityComponentAssign')

    def validate(self):
        int(self.RequestInfo['componentID'])
        int(self.RequestInfo['activityID'])
        int(self.RequestInfo['actTypeCompTypeID'])
        int(self.RequestInfo['userID'])


class ActivityComponentRemove(DBRemoveRequest):
    Request = getattr(client.service, 'ActivityComponentRemove')


class ActivityCreate(DBRequest):
    Request = getattr(client.service, 'ActivityCreate')

    def validate(self):
        int(self.RequestInfo['activityTypeID'])
        int(self.RequestInfo['locationID'])
        self.RequestInfo['lotID']  # string
        self.RequestInfo['activityName']  # string
        self.RequestInfo['startDate']  # string
        self.RequestInfo['endDate']  # string
        self.RequestInfo['position']  # string
        int(self.RequestInfo['resultID'])
        int(self.RequestInfo['statusID'])
        int(self.RequestInfo['userID'])


class ActivityChange(DBRequest):
    Request = getattr(client.service, 'ActivityChange')

    def validate(self):
        int(self.RequestInfo['ID'])
        int(self.RequestInfo['activityTypeID'])
        int(self.RequestInfo['locationID'])
        self.RequestInfo['lotID']  # string
        self.RequestInfo['activityName']  # string
        self.RequestInfo['startDate']  # string
        self.RequestInfo['endDate']  # string
        self.RequestInfo['position']  # string
        int(self.RequestInfo['resultID'])
        int(self.RequestInfo['statusID'])
        int(self.RequestInfo['userID'])


class ActivityMemberAssign(DBRequest):
    Request = getattr(client.service, 'ActivityMemberAssign')

    def validate(self):
        int(self.RequestInfo['projectMemberID'])
        int(self.RequestInfo['activityID'])
        int(self.RequestInfo['leader'])
        int(self.RequestInfo['userID'])


class ActivityMemberChange(DBRequest):
    Request = getattr(client.service, 'ActivityMemberChange')

    def validate(self):
        int(self.RequestInfo['ID'])
        int(self.RequestInfo['leader'])
        int(self.RequestInfo['userID'])


class ActivityMemberRemove(DBRemoveRequest):
    Request = getattr(client.service, 'ActivityMemberRemove')


class ActivityParameterCreate(DBRequest):
    Request = getattr(client.service, 'ActivityParameterCreate')

    def validate(self):
        int(self.RequestInfo['activityID'])
        int(self.RequestInfo['activityParameterID'])
        float(self.RequestInfo['value'])
        int(self.RequestInfo['userID'])


class ActivityParameterChange(DBRequest):
    Request = getattr(client.service, 'ActivityParameterChange')

    def validate(self):
        int(self.RequestInfo['ID'])
        float(self.RequestInfo['value'])
        int(self.RequestInfo['userID'])


class ActivityParameterRemove(DBRemoveRequest):
    Request = getattr(client.service, 'ActivityParameterRemove')


class ActivityUriCreate(DBRequest):
    Request = getattr(client.service, 'ActivityUriCreate')

    def validate(self):
        int(self.RequestInfo['activityID'])
        self.RequestInfo['uriPath']  # string
        self.RequestInfo['uriDescription']  # string
        int(self.RequestInfo['userID'])


class ActivityUriChange(DBRequest):
    Request = getattr(client.service, 'ActivityUriChange')

    def validate(self):
        int(self.RequestInfo['activitysUriID'])
        self.RequestInfo['uriPath']  # string
        self.RequestInfo['uriDescription']  # string
        int(self.RequestInfo['userID'])


class ActivityUriRemove(DBRequest):
    Request = getattr(client.service, 'ActivityUriRemove')

    def validate(self):
        int(self.RequestInfo['uriID'])


class ComponentCreate(DBRequest):
    Request = getattr(client.service, 'ComponentCreate')

    def validate(self):
        int(self.RequestInfo['componentTypeID'])
        self.RequestInfo['componentID']  # string
        self.RequestInfo['supplierComponentID']  # string
        self.RequestInfo['description']  # string
        self.RequestInfo['lotID']  # string
        self.RequestInfo['packageID']  # string
        int(self.RequestInfo['userID'])


class ComponentChange(DBRequest):
    Request = getattr(client.service, 'ComponentChange')

    def validate(self):
        int(self.RequestInfo['ID'])
        int(self.RequestInfo['componentTypeID'])
        self.RequestInfo['componentId']  # string
        self.RequestInfo['supplierComponentId']  # string
        self.RequestInfo['description']  # string
        self.RequestInfo['lotID']  # string
        self.RequestInfo['packageID']  # string
        int(self.RequestInfo['userID'])


class ComponentRemove(DBRemoveRequest):
    Request = getattr(client.service, 'ComponentRemove')


class ComponentCompositionCreate(DBRequest):
    Request = getattr(client.service, 'ComponentCompositionCreate')

    def validate(self):
        int(self.RequestInfo['rootID'])
        int(self.RequestInfo['ID'])
        self.RequestInfo['position']
        int(self.RequestInfo['userID'])


class ComponentCompositionPositionChange(DBRequest):
    Request = getattr(client.service, 'ComponentCompositionPositionChange')

    def validate(self):
        int(self.RequestInfo['ID'])
        self.RequestInfo['position']
        int(self.RequestInfo['userID'])


class ComponentCompositionRemove(DBRemoveRequest):
    Request = getattr(client.service, 'ComponentCompositionRemove')


################################################################
# Reads
################################################################
class ActivityRead(DBRequest):
    """
    Get all instances of a particular activity type
    """
    Request = getattr(client.service, 'ActivityRead')

    def validate(self):
        int(self.RequestInfo['projectID'])
        int(self.RequestInfo['activityTypeID'])


class ActivityReadOne(DBRequest):
    """
    Get all information about a particular activity
    """
    Request = getattr(client.service, 'ActivityReadOne')

    def validate(self):
        int(self.RequestInfo['ID'])


class ActivityTypeRead(DBRequest):
    """
    Get some information about all activity types
    """
    Request = getattr(client.service, 'ActivityTypeRead')

    def validate(self):
        int(self.RequestInfo['projectID'])


class ActivityTypeReadAll(DBRequest):
    """
    Get all information about a particular activity type
    """
    Request = getattr(client.service, 'ActivityTypeReadAll')

    def validate(self):
        int(self.RequestInfo['activityTypeID'])


class AttachmentCategoryRead(DBRequest):
    """
    Get information about all attachment categories (ID, category, description)
    """
    Request = getattr(client.service, 'AttachmentCategoryRead')

    def validate(self):
        assert not self.RequestInfo


class ComponentActivityHistoryRead(DBRequest):
    """
    Get full activity history for a given component
    """
    Request = getattr(client.service, 'ComponentActivityHistoryRead')

    def validate(self):
        int(self.RequestInfo['ID'])


class ComponentChildrenRead(DBRequest):
    """
    Get information about children of a given component
    """
    Request = getattr(client.service, 'ComponentChildrenRead')

    def validate(self):
        int(self.RequestInfo['ID'])


class ComponentParentRead(DBRequest):
    """
    Get information about parent(s?) of a given component
    """
    Request = getattr(client.service, 'ComponentParentRead')

    def validate(self):
        int(self.RequestInfo['ID'])


class ComponentRead(DBRequest):
    """
    Get all instances of a particular component type
    """
    Request = getattr(client.service, 'ComponentRead')

    def validate(self):
        int(self.RequestInfo['projectID'])
        int(self.RequestInfo['componentTypeID'])


class ComponentReadOne(DBRequest):
    """
    Get all information about a particular component
    """
    Request = getattr(client.service, 'ComponentReadOne')

    def validate(self):
        int(self.RequestInfo['ID'])
        self.RequestInfo['componentID']


class ComponentTypeRead(DBRequest):
    """
    Get some information about all component types
    """
    Request = getattr(client.service, 'ComponentTypeRead')

    def validate(self):
        int(self.RequestInfo['projectID'])


class ComponentTypeReadAll(DBRequest):
    """
    Get all information about a particular component type
    """
    Request = getattr(client.service, 'ComponentTypeReadAll')

    def validate(self):
        int(self.RequestInfo['componentTypeID'])


class ProjectMemberRead(DBRequest):
    """
    Get all members (ID, PersonID, FullName) of a particular project
    """
    Request = getattr(client.service, 'ProjectMemberRead')

    def validate(self):
        int(self.RequestInfo['projectID'])


class ProjectRead(DBRequest):
    """
    Get all project information (ID, Name)
    """
    Request = getattr(client.service, 'ProjectRead')

    def validate(self):
        assert not self.RequestInfo


class ReadComponentWithParent(DBRequest):
    """
    (?) Get all information about a particular component type and its parent
    """
    Request = getattr(client.service, 'ReadComponentWithParent')

    def validate(self):
        int(self.RequestInfo['componentTypeID'])
        self.RequestInfo['parentTypeID']
