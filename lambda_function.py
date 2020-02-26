"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import boto3

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the vister checking system. " 
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your query by saying, " 
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_help_response():
    session_attributes = {}
    card_title = "welcome"
    speech_output = "You can ask me who come to visit me on year month day. "
    reprompt_text = "Don't be stupid. "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using vister check system. " \
                    "If you find someone unwelcomed visited, please call 911 "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

#-----------------comparing face called by vister_check----------------------

def compare_face(mydate):
    s3 = boto3.resource('s3')
	#The string list below is initialize as "no one", it will be add some names if the face is found
	#It will also be return by this function
    visiters = set(['no one'])
    client=boto3.client('rekognition')
    
    source1 = 'example.jpg'
    sourceBucket = 'yoursourcebucket'
    
    targetBucket = s3.Bucket('yourtargetcamera')
    targetBucketName = 'yourtargetcamera'
	#------------------------------------------------------------------------------------------
	#so far, didn't find a better way to return the picutre file name as a string without extension,
	#if any other image upload to database, need run the code between two lines one more time
	#and change all "chenjun" to the "guy's name", also need add one more code is:
	#source1 = "The new source face image"
    for obj in targetBucket.objects.all():
        date = obj.key
        index = date.find(mydate)
        if index>-1:
            
            findFace = client.detect_faces(Image={'S3Object':{'Bucket':targetBucketName,'Name':date}},Attributes=['ALL'])
            
            for faceDetail in findFace['FaceDetails']:
                if faceDetail['Confidence']>98:
                    response=client.compare_faces(SimilarityThreshold=70,
                                          SourceImage={'S3Object':{'Bucket':sourceBucket,'Name':source1}},
                                          TargetImage={'S3Object':{'Bucket':targetBucketName,'Name':date}})
                    for faceMatch in response['FaceMatches']:
                        if 'no one' in visiters:
                            visiters.add('examplename')
                            visiters.remove('no one')
                        else:
                            visiters.add('examplename')
                    for faceUnmatch in response['UnmatchedFaces']:
                        if 'no one' in visiters:
                            visiters.add('Stranger')
                            visiters.remove('no one')
                        else:
                            visiters.add('Stranger')
	#repeat code until here
	#-------------------------------------------------------------------------------------------
    return visiters
                        
    
#-----------------called by handler------------------------------------    


def vister_check(intent, session):

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = None

#check if the date contain in targets' file name
#The date here is send by intent[slot], the slot just return an amazon_number
#It's not easy for user but easy for coding.
#The user can't say 2019 May first. He has to say two zero one nine zero five zero one
    if 'yeardate' in intent['slots']:
        date = intent['slots']['yeardate']['value']
        whocome = compare_face(date)
        speech_output = "visited you. "
        for who in whocome:
            speech_output = who + ", " + speech_output

        reprompt_text = "I'm not going to talk. "
    else:
        speech_output = "Please say who come to visit me on year month and day. "
        reprompt_text = "You idot. " 
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "WhoCome":
        return vister_check(intent, session)
 
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):

    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
