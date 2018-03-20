from locust import HttpLocust, TaskSet, task
import hashlib
import hmac
import time


class UserBehavior(TaskSet):

    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.sessionId = 'abcd'
        self.jsonPayload = "{'abc':'def'}"
        self.timestamp = time.time()*1000
        self.parameters = ''
        self.sessionKey = 'ghi'
        self.login()

    def login(self):
        # self.client.post(
        #     "/login", {"username": "ellen_key", "password": "education"})
        response = self.client.get(
            "/api/latest/accounts/user/session/credentials?userEmail=hark.portal.user@gmail.com&userPassword=q2w3e4r5%21")
        json_response_dict = response.json()
        self.sessionId = json_response_dict['sessionId']
        self.sessionKey = json_response_dict['sessionKey']

    @task(2)
    def userId(self):
        print("yo dad!")
        harkHeaders = self.buildHarkHeaders(
            'GET', '/api/latest/accounts/userId', self.sessionId, self.jsonPayload, self.timestamp, self.parameters, self.sessionKey)
        print(harkHeaders)
        response = self.client.get(
            "/api/latest/accounts/userId", headers=harkHeaders)
        print(response)
        print(response.json())

    # @task(1)
    # def profile(self):
    #     self.client.get("/profile")

    def buildHarkHeaders(self, httpMethod, path, sessionId, jsonPayload, timestamp, parameters, sessionKey):
        harkAuthHeaders = {}
        jsonPayloadHash = hashlib.sha256(
            bytes(jsonPayload.encode())).hexdigest()
        print('jsonPayloadHash: '+jsonPayloadHash)

        signaturePayload = []
        signaturePayload.append(httpMethod)
        signaturePayload.append(path)
        signaturePayload.append('hark-auth-session-id:'+sessionId)
        signaturePayload.append('hark-auth-timestamp:'+str(int(timestamp)))
        signaturePayload.append(parameters)
        signaturePayload.append(jsonPayloadHash)
        print(signaturePayload)

        # butFirst = signaturePayload[1:]
        signaturePayloadMultiLineString = "\n".join(signaturePayload)
        print('signaturePayloadMultiLineString: ' +
              signaturePayloadMultiLineString)

        signaturePayloadHash = hashlib.sha256(
            signaturePayloadMultiLineString.encode('utf8')).hexdigest()
        print('signaturePayloadHash: '+signaturePayloadHash)
        print('sessionKey: '+sessionKey)
        signingKey = hmac.new(bytes(sessionKey.encode(
            'utf-8')), signaturePayloadHash.encode(
            'utf-8'), digestmod=hashlib.sha256).digest()
        print(signingKey)

        harkAuthSignature = signingKey.hex()
        # print('harkAuthSignature: '+harkAuthSignature)

        harkAuthHeaders['hark-auth-session-id'] = sessionId
        harkAuthHeaders['hark-auth-timestamp'] = str(int(timestamp))
        harkAuthHeaders['hark-auth-signature'] = harkAuthSignature
        return harkAuthHeaders


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
