from locust import HttpLocust, TaskSet, task
import json

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.getQuestionnaire()
        # self.getUser()

    def on_stop(self):
        """ on_stop is called when the TaskSet is stopping """
        self.getReport()

    @task
    def getUser(self):
        userId = 28
        respUser = self.client.get("/user?userId=%s" % userId)
        print("respUser=%s" % respUser)
        if respUser:
            respUserText = respUser.text
            print("respUserText=%s" % respUserText)
            respUserJson = json.loads(respUserText)
            print("respUserJson=%s" % respUserJson)

    @task
    def getQuestionnaire(self):
        respQuestionnaire = self.client.get("/user/questionnaire")
        if respQuestionnaire:
            print("respQuestionnaire=%s" % respQuestionnaire)
            respQuestionnaireText = respQuestionnaire.text
            print("respQuestionnaireText=%s" % respQuestionnaireText)
            respQuestionnaireJson = json.loads(respQuestionnaireText)
            print("respQuestionnaireJson=%s" % respQuestionnaireJson)

    @task
    def getReport(self):
        eval_id = "5c32f7131275880273f5ee25"
        action = "getReport"
        self.client.get("/evaluation?eval_id=%s&action=%s" % (eval_id, action))

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 1000
    max_wait = 5000