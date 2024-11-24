# All names and functions have been kept as close as possible to the original, to make conversion easier
# For simplicity and my sanity, types aren't included in this version of the library, maybe for a later version
# TODO -> Maybe refactor self.config and replace it with independant attributes 

# Base 64
import base64
# Basic types
from typing import Optional, List, Dict, Union, Any
# Json handling
import json
# Replace axios with requests
import requests
from requests.exceptions import HTTPError
# Replace oid-client with authlib
from authlib.integrations.requests_client import OAuth2Session
# Import error modules
from errors import *
# Import serialize and deserialize module
from json_api_doc import serialize, deserialize


BASE_URL = 'https://api.skolengo.com/api/v1/bff-sko-app'
OID_CLIENT_ID = base64.b64decode('U2tvQXBwLlByb2QuMGQzNDkyMTctOWE0ZS00MWVjLTlhZjktZGY5ZTY5ZTA5NDk0').decode('utf-8') # base64 du client ID de l'app mobile
OID_CLIENT_SECRET = base64.b64decode('N2NiNGQ5YTgtMjU4MC00MDQxLTlhZTgtZDU4MDM4NjkxODNm').decode('utf-8') # base64 du client Secret de l'app mobile
REDIRECT_URI = 'skoapp-prod://sign-in-callback'


class Skolengo:

    def __init__(self,
                 oidClient,
                 school,
                 tokenSet,
                 config=None) -> None:
        
        self.oidClient = oidClient[0]
        self.oidClientConfig = oidClient[1]
        self.school = school
        self.tokenSet = tokenSet
        self.config = config or {}

        self.config = {
            "httpClient": config.get("httpClient", requests.Session()),
            "onTokenRefresh": config.get("onTokenRefresh", self.onRefreshToken),
            "refreshToken": config.get("refreshToken", self.refreshToken),
            "handlePronoteError": config.get("handlePronoteError", True)
        }
        
        # Set the base URL for the session's requests
        self.config["httpClient"].base_url = BASE_URL 

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        Useful for initializing resources or setup logic.
        """
        # Perform any setup if needed (e.g., logging, validating tokens)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object.
        Useful for cleanup logic.
        """
        # Perform any cleanup if needed (e.g., closing HTTP sessions)
        if hasattr(self, "config") and "httpClient" in self.config:
            httpClient = self.config["httpClient"]
            if isinstance(httpClient, requests.Session):
                httpClient.close()
        # Optionally handle exceptions
        if exc_type:
            print(f"Exception occurred: {exc_value}")
        # Return False to propagate exceptions, True to suppress them
        return False

    def revokeToken(oidClient, url, token):
        """
        url: the token endpoint url, has to be https
        """
        oidClient.revoke_token(url, token)

    def getAppCurrentConfig(httpConfig={}):
        response = requests.get(f"{BASE_URL}/sko-app-configs/current",
                                **httpConfig)
        
        return deserialize(response.json())

    def searchSchool(filter,
                     limit=10,
                     offset=0,
                     httpConfig={}):
        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[text]": filter
        }

        response = requests.get(f"{BASE_URL}/schools",
                                params=params,
                                **httpConfig)
        
        return deserialize(response.json())
    
    def getOIDClient(school, redirectUri = 'skoapp-prod://sign-in-callback'):
        if school['emsOIDCWellKnownUrl'] == None: 
            raise TypeError('emsOIDCWellKnownUrl invalid')

        response = requests.get(school['emsOIDCWellKnownUrl'])
        response.raise_for_status()  # Ensure the request was successful
        config = response.json()
        # print(config)

        # Create an OAuth2 session using the metadata
        oauth = OAuth2Session(
            client_id=OID_CLIENT_ID,
            redirect_uri=redirectUri,
            authorization_url=config["authorization_endpoint"],
            token_url=config["token_endpoint"])

        # Set the client secret manually (authlib doesn’t automatically handle this)
        oauth.client_secret = OID_CLIENT_SECRET

        return oauth, config
    
    def fromConfigObject(config, skolengoConfig = {}):
        return Skolengo(Skolengo.getOIDClient(config["school"]), config["school"], config["tokenSet"], skolengoConfig)
            # return Skolengo(None, config["school"], config["tokenSet"], skolengoConfig)
        
    def getUserInfo(self,
                    userId = None,
                    params = None,
                    includes = ['school', 'students', 'students.school', 'schools', 'prioritySchool']):
        
        params = {} if params is None else params
        userId = self.getTokenClaims().get("sub") if userId is None else userId

        params["include"] = ",".join(includes)

        response = self.request({
            "url": f'/users-info/{userId}',
            "method": 'get',
            "params": params
        })

        return deserialize(response)
    
    # To test
    def downloadAttachment(self, attachment):
        return self.request(attachment['url']).json()['data']
    
    def getSchoolInfos(self,
                       params = None, 
                       includes = ['illustration', 'school', 'author', 'author.person', 'author.technicalUser', 'attachments']):
        
        params = {} if params is None else params

        params["include"] = ",".join(includes)

        response = self.request({
            "url": '/schools-info',
            "method": 'get',
            "params": params
        })

        return deserialize(response)
    
    # Link doesn't work in this library and js library
    def getSchoolInfo(self,
                      schoolInfoId = None,
                      params = None, 
                      includes = ['illustration', 'school', 'author', 'author.person', 'author.technicalUser', 'attachments']):
        
        schoolInfoId = self.school['id'] if schoolInfoId is None else schoolInfoId
        params = {} if params is None else params

        params["include"] = ",".join(includes)

        response = self.request({
            "url": f'/schools-info/{schoolInfoId}',
            "method": 'get',
            "params": params
        })

        return deserialize(response)
    
    def getEvaluationSettings(self,
                              studentId = None,
                              limit = 20,
                              offset = 0,
                              params = None,
                              includes = ['periods', 'skillsSetting', 'skillsSetting.skillAcquisitionColors']):
        
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId
        params = {} if params is None else params

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[student.id]": studentId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/evaluations-settings',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    # Requires Pronote resources, whatever that is
    # Doesn't work for now
    def getEvaluation(self,
                      periodId,
                      studentId = None,
                      limit = 20,
                      offset = 0,
                      params = None,
                      includes = ['subject', 'evaluations', 'evaluations.evaluationResult', 'evaluations.evaluationResult.subSkillsEvaluationResults', 'evaluations.evaluationResult.subSkillsEvaluationResults.subSkill', 'evaluations.subSkills', 'teachers']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[student.id]": studentId,
            "filter[period.id]": periodId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/evaluation-services',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    # Can't check if it works since  I can't get getEvaluation to work 
    def getEvaluationDetail(self,
                            evaluationId,
                            studentId = None,
                            params = None,
                            includes = ['evaluationService', 'evaluationService.subject', 'evaluationService.teachers', 'subSubject', 'subSkills', 'evaluationResult', 'evaluationResult.subSkillsEvaluationResults', 'evaluationResult.subSkillsEvaluationResults.subSkill']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "filter[student.id]": studentId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": f'/evaluations/{evaluationId}',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    # Forbidden for my school, can't test it
    def getPeriodicReportsFiles(self,
                                studentId = None,
                                limit = 20,
                                offset = 0,
                                params = None,
                                includes = ['period']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[student.id]": studentId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/periodic-reports-files',
            "method": 'get',
            "params": params
        })

        return deserialize(response)


    def getAgenda(self,
                  startDate,
                  endDate,
                  studentId = None,
                  limit = 20,
                  offset = 0,
                  params = None,
                  includes = ['lessons', 'lessons.subject', 'lessons.teachers', 'homeworkAssignments', 'homeworkAssignments.subject']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[student.id]": studentId,
            "filter[date][GE]": startDate,
            "filter[date][LE]": endDate,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/agendas',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    def getLesson(self,
                  lessonId,
                  studentId = None,
                  params = None,
                  includes = ['teachers', 'contents', 'contents.attachments', 'subject', 'toDoForTheLesson', 'toDoForTheLesson.subject', 'toDoAfterTheLesson', 'toDoAfterTheLesson.subject']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "filter[student.id]": studentId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": f'/lessons/{lessonId}',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    def getHomeworkAssignments(self,
                               startDate,
                               endDate,
                               studentId = None,
                               limit = 20,
                               offset = 0,
                               params = None,
                               includes = ['subject', 'teacher', 'teacher.person']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[student.id]": studentId,
            "filter[dueDate][GE]": startDate,
            "filter[dueDate][LE]": endDate,
            "fields[homework]": 'title,done,dueDateTime,html',
            "fields[subject]": 'label,color',
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/homework-assignments',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    def getHomeworkAssignment(self,
                              homeworkId,
                              studentId = None,
                              params = None,
                              includes = ['subject', 'teacher', 'pedagogicContent', 'individualCorrectedWork', 'individualCorrectedWork.attachments', 'individualCorrectedWork.audio', 'commonCorrectedWork', 'commonCorrectedWork.attachments', 'commonCorrectedWork.audio', 'commonCorrectedWork.pedagogicContent', 'attachments', 'audio', 'teacher.person']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "filter[student.id]": studentId,
            "fields[homework]": 'title,done,dueDateTime,html',
            "fields[subject]": 'label,color',
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": f'/homework-assignments/{homeworkId}',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    def patchHomeworkAssignment(self,
                                homeworkId,
                                attributes,
                                studentId = None,
                                params = None,
                                includes = ['subject', 'teacher', 'pedagogicContent', 'individualCorrectedWork', 'individualCorrectedWork.attachments', 'individualCorrectedWork.audio', 'commonCorrectedWork', 'commonCorrectedWork.attachments', 'commonCorrectedWork.audio', 'commonCorrectedWork.pedagogicContent', 'attachments', 'audio', 'teacher.person']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "filter[student.id]": studentId,
            "include": ','.join(includes),
            **params
        }

        data = {
            "data": {
                "type": 'homework',
                "id": homeworkId,
                "attributes": attributes
            }
        }

        response = self.request({
            "url": f'/homework-assignments/{homeworkId}',
            "method": 'patch',
            "params": params,
            "data": json.dumps(data)
        })

        return deserialize(response)

    def getUsersMailSettings(self,
                             userId = None,
                             params = None,
                             includes = ['signature', 'folders', 'folders.parent', 'contacts', 'contacts.person', 'contacts.personContacts']):
        
        params = {} if params is None else params
        userId = self.getTokenClaims().get("sub") if userId is None else userId

        params = {
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": f'/users-mail-settings/{userId}',
            "method": 'get',
            "params": params,
        })

        return deserialize(response)

    def getCommunicationsFolder(self,
                                folderId,
                                limit = 10,
                                offset = 0,
                                params = None,
                                includes = ['lastParticipation', 'lastParticipation.sender', 'lastParticipation.sender.person', 'lastParticipation.sender.technicalUser']):
        
        params = {} if params is None else params

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[folders.id]": folderId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/communications',
            "method": 'get',
            "params": params,
        })

        return deserialize(response)

    def getCommunication(self,
                         communicationId,
                         params = None):
        
        params = {} if params is None else params

        response = self.request({
            "url": f'/communications/{communicationId}',
            "method": 'get',
            "params": params,
        })

        return deserialize(response)

    def getCommunicationParticipations(self,
                                       communicationId,
                                       params = None,
                                       includes = ['sender', 'sender.person', 'sender.technicalUser', 'attachments']):
        
        params = {} if params is None else params

        params["include"] = ",".join(includes)

        response = self.request({
            "url": f'/communications/{communicationId}/participants',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    def getCommunicationParticipants(self,
                                     communicationId,
                                     fromGroup = True,
                                     params = None,
                                     includes = ['sender', 'sender.person', 'sender.technicalUser', 'attachments']):
        
        params = {} if params is None else params

        params = {
            "filter[fromGroup]": fromGroup,
            "include": ",".join(includes),
            **params
        }

        response = self.request({
            "url": f'/communications/{communicationId}/participations',
            "method": 'get',
            "params": params,
        })

        return deserialize(response)

    def patchCommunicationFolders(self,
                                  communicationId,
                                  folders,
                                  userId = None,
                                  params = None):
        
        params = {} if params is None else params
        userId = self.getTokenClaims().get("sub") if userId is None else userId

        params = {
            "filter[user.id]": userId,
            **params
        }

        response = self.request({
            "url": f'/communications/{communicationId}/relationships/folders',
            "method": 'patch',
            "params": params,
            "data": json.dumps({"data": folders})
        })

        return deserialize(response)

    def postCommunication(self,
                          newCommunication,
                          params = None):
        
        params = {} if params is None else params

        response = self.request({
            "url": f'/communications',
            "method": 'post',
            "params": params,
            "data": json.dumps({"data": newCommunication})
        })

        return deserialize(response)
                          
    def postParticipation(self,
                          participation,
                          params = None):
        
        params = {} if params is None else params

        response = self.request({
            "url": f'/participations',
            "method": 'post',
            "params": params,
            "data": json.dumps({"data": participation})
        })

        return deserialize(response)

    # Couldn't get it working because of PRONOTE_RESOURCES_NOT_READY
    def getAbsenceFiles(self,
                        studentId = None,
                        limit = 20,
                        offset = 0,
                        params = None,
                        includes = ['currentState', 'currentState.absenceReason', 'currentState.absenceRecurrence']):
        
        params = {} if params is None else params
        studentId = self.getTokenClaims().get("sub") if studentId is None else studentId

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            "filter[student.id]": studentId,
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": '/absence-files',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    def getAbsenceFile(self,
                       folderId,
                       params = None,
                       includes = ['currentState', 'currentState.absenceReason', 'currentState.absenceRecurrence', 'history', 'history.creator']):
        
        params = {} if params is None else params

        params = {
            "include": ','.join(includes),
            **params
        }

        response = self.request({
            "url": f'/absence-files/{folderId}',
            "method": 'get',
            "params": params
        })

        return deserialize(response)

    # Haven't tested this either
    # Should the method be post, since it isn't in the js library?
    def postAbsenceFileState(self,
                             folderId,
                             reasonId,
                             comment,
                             params = None):
        
        params = {} if params is None else params

        data = {
            serialize({
                    "comment": comment,
                    "absenceFile": {
                        "id": folderId
                    },
                    "absenceReason": {
                        "id": reasonId
                    }
                }, 'absenceFileState', {
                "relationships": ['absenceFile', 'absenceReason']
                }
            )
        }

        response = self.request({
            "url": f'/absence-files-states',
            "method": 'post',
            "params": params,
            "data": data
        })

        return deserialize(response)

    def getAbsenceReasons(self,
                          limit = 20,
                          offset = 0,
                          params = None):
        
        params = {} if params is None else params

        params = {
            "page[limit]": limit,
            "page[offset]": offset,
            **params
        }

        response = self.request({
            "url": f'/absence-reasons',
            "method": 'get',
            "params": params,
        })

        return deserialize(response)

    def refreshToken(self, triggerListener = True):
        # Refresh token on config
        if self.config['refreshToken'] is None:
            self.tokenSet = self.config['refreshToken'](self.tokenSet)

            # Execute event listener if onTokenRefresh is defined
            if triggerListener:
                self.config['onTokenRefresh']()

            return self.tokenSet
        
        if self.oidClient is None:
            raise Exception('Impossible de rafraîchir le jeton sans le client OpenID Connect.')

        self.tokenSet = self.oidClient.refresh_token(self.oidClientConfig['token_endpoint'],
                                         refresh_token=self.tokenSet['refresh_token'],
                                         client_secret=self.oidClient.client_secret)

        if triggerListener:
            self.config['onTokenRefresh']()

        return self.tokenSet
    
    # Dummy function for trigger listener
    def onRefreshToken(self):
        ...

    def getTokenClaims(self):
        if self.tokenSet.get('id_token') is None:
            raise TypeError('id_token not present in TokenSet')
        
        data = self.tokenSet.get('id_token').split('.')
        data_part = data[1].replace('-', '+').replace('_', '/') if len(data) > 1 else None

        if data_part is None or len(data_part.strip()) == 0:
            raise TypeError('Invalid id_token')

        return json.loads(base64.b64decode(data_part + "==").decode('utf-8'))
        
    def onPronoteError(self,
                       config,
                       maxRetries = 5):
        
        for i in range(maxRetries):
            try:
                response = self.config["httpClient"].request(**config)
                response.raise_for_status()
                return response.json()
            
            except HTTPError as error:
                if error.name != 'PRONOTE_RESOURCES_NOT_READY':
                    raise error
                
        response = self.config["httpClient"].request(**config)
        return response.json() 

    def request(self, config):
        """
        Perform an HTTP request with token-based authentication and error handling.
        """

        # Building the headers
        headers = {
            'Authorization': f"Bearer {self.tokenSet["access_token"]}",
            'X-Skolengo-Date-Format': 'utc',
            'X-Skolengo-School-Id': self.school['id'],
            'X-Skolengo-Ems-Code': self.school['emsCode']
        }

        # Config
        # Default structure should be:
        # config = {
        #   url: BASE_URL + url,
        #   method: method,
        #   headers: headers,
        #   params: params
        # }
        # Change url in config
        config["url"] = f"{BASE_URL}{config['url']}"
        # Add the headers
        config["headers"] = headers
 
        try:
            # Make the HTTP request
            response = self.config["httpClient"].request(**config)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.json()
        
        except HTTPError as error:
            response = error.response
            
            if response is None:
                raise error
            
            if response.status_code == 401:
                self.refreshToken()

                headers["Authorization"] = f"Bearer {self.tokenSet['access_token']}"
                response = self.config["httpClient"].request(**config)
                return response.json()
            
            if response.status_code == 404:
                raise error

            if "errors" in response.json() and isinstance(response.json()["errors"], list):
                first_error = response.json()["errors"][0]
                skolengoError = SkolengoError(first_error)

                if self.config.get("handlePronoteError", False) and skolengoError.name == "PRONOTE_RESOURCES_NOT_READY":
                    return self.onPronoteError(config)
                
                raise skolengoError
            
            raise error
